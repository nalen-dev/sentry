//! Sync agent: membaca unit DTS lokal (MySQL + SQLite desktop) lalu mengirim ke API cloud.
//!
//! - live      : tiap DTS_LIVE_INTERVAL_SECS, dikirim langsung (tidak diantrekan)
//! - history   : agregat 1 menit, lewat antrean offline
//! - alarm     : TRIGGERED/CLEARED dari threshold, ACKNOWLEDGED dari alarmlog; lewat antrean, prioritas
//! - segments  : saat start, saat konfigurasi berubah, dan tiap 6 jam; lewat antrean

mod aggregator;
mod cloud;
mod config;
mod curve;
mod outbox;
mod source;
mod status;

use std::{
    collections::{HashMap, HashSet},
    sync::Arc,
    time::{Duration, Instant},
};

use chrono::Utc;
use dts_shared::{
    AlarmEventType, IngestAlarm, IngestHistory, IngestLive, IngestSegments, LivePointSample,
    LiveSegmentSample, SegmentInfo, SegmentKey, SegmentStatus,
};
use reqwest::Method;
use sqlx::{mysql::MySqlPoolOptions, MySqlPool, SqlitePool};
use uuid::Uuid;

use aggregator::Aggregator;
use cloud::{Cloud, SendError};
use config::Config;
use outbox::{Outbox, KIND_ALARM, KIND_HISTORY, KIND_SEGMENTS};
use status::{next_level, Level};

const SEGMENT_RESYNC: Duration = Duration::from_secs(6 * 3600);
/// Nilai mentah DTS <= -2000 (mis. -2731) berarti tidak ada sensor pada segmen tersebut.
const NO_SENSOR_C: f32 = -200.0;

struct Ctx {
    sqlite: SqlitePool,
    mysql: MySqlPool,
    outbox: Outbox,
    cloud: Arc<Cloud>,
}

#[derive(Default)]
struct State {
    levels: HashMap<SegmentKey, Level>,
    agg: Aggregator,
    segments_json: String,
    segments_synced_at: Option<Instant>,
    ack_max_id: Option<i32>,
    ack_open: HashSet<i32>,
    live_ok: Option<bool>,
}

#[tokio::main]
async fn main() {
    let cfg = Config::from_env().unwrap_or_else(|e| {
        eprintln!("konfigurasi tidak valid: {e}");
        std::process::exit(1);
    });
    let sqlite = source::open_sqlite(&cfg.sqlite_path).await.unwrap_or_else(|e| {
        eprintln!("tidak bisa membuka {}: {e}", cfg.sqlite_path.display());
        std::process::exit(1);
    });
    let my_opts = source::mysql_options(&sqlite, &cfg.mysql).await.unwrap_or_else(|e| {
        eprintln!("konfigurasi MySQL: {e}");
        std::process::exit(1);
    });
    // Lazy: agent tetap hidup walau unit DTS belum menyala saat start.
    let mysql = MySqlPoolOptions::new()
        .max_connections(3)
        .acquire_timeout(Duration::from_secs(5))
        .connect_lazy_with(my_opts);
    let outbox = Outbox::open(&cfg.queue_path).await.unwrap_or_else(|e| {
        eprintln!("tidak bisa membuka antrean {}: {e}", cfg.queue_path.display());
        std::process::exit(1);
    });
    let cloud = Arc::new(Cloud::new(cfg.cloud_url.clone(), cfg.api_key.clone(), cfg.dry_run));

    println!(
        "dts-agent mulai (interval live {}s{}), antrean: {}",
        cfg.live_interval.as_secs(),
        if cfg.dry_run { ", DRY-RUN" } else { "" },
        cfg.queue_path.display()
    );
    tokio::spawn(cloud::run_sender(outbox.clone(), cloud.clone()));

    let ctx = Ctx { sqlite, mysql, outbox, cloud };
    let mut st = State::default();
    match ctx.outbox.load_levels().await {
        Ok(rows) => {
            for (ch, code, lvl) in rows {
                st.levels.insert(SegmentKey { dts_ch: ch, dts_code: code }, Level::from_i32(lvl));
            }
            println!("level alarm dipulihkan untuk {} segmen", st.levels.len());
        }
        Err(e) => eprintln!("[outbox] gagal memuat level alarm: {e}"),
    }
    let mut tick = tokio::time::interval(cfg.live_interval);
    tick.set_missed_tick_behavior(tokio::time::MissedTickBehavior::Skip);
    loop {
        tick.tick().await;
        if let Err(e) = cycle(&ctx, &mut st).await {
            eprintln!("[siklus] {e}");
        }
    }
}

fn status_of(level: Level) -> SegmentStatus {
    level.into()
}

async fn enqueue_json<T: serde::Serialize>(ctx: &Ctx, kind: &str, value: &T) {
    match serde_json::to_string(value) {
        Ok(json) => {
            if let Err(e) = ctx.outbox.enqueue(kind, &json).await {
                eprintln!("[outbox] gagal menyimpan {kind}: {e}");
            }
        }
        Err(e) => eprintln!("[outbox] gagal serialisasi {kind}: {e}"),
    }
}

async fn cycle(ctx: &Ctx, st: &mut State) -> Result<(), String> {
    let e = |what: &str, err: sqlx::Error| format!("{what}: {err}");
    let mappings = source::mappings(&ctx.sqlite).await.map_err(|x| e("baca segment_mappings", x))?;
    let (warning, critical) = source::thresholds(&ctx.sqlite).await.map_err(|x| e("baca threshold", x))?;

    sync_segments(ctx, st, &mappings).await;

    let rows = source::live(&ctx.mysql).await.map_err(|x| e("baca opt_fq_list (unit DTS tidak terjangkau?)", x))?;
    let live_by_key: HashMap<(i32, i32), &source::LiveRow> = rows.iter().map(|r| ((r.ch, r.code), r)).collect();

    let now = Utc::now();
    let mut segments = Vec::new();
    let mut samples = Vec::new();
    for m in &mappings {
        let Some(l) = live_by_key.get(&(m.dts_ch, m.dts_code)) else { continue };
        let c = |v: Option<i32>| v.unwrap_or(0) as f32 / 10.0;
        let (avg, min, max) = (c(l.temp_avg), c(l.temp_min), c(l.temp_max));
        if avg < NO_SENSOR_C || max < NO_SENSOR_C {
            continue; // segmen tanpa sensor
        }
        let key = SegmentKey { dts_ch: m.dts_ch, dts_code: m.dts_code };

        let prev = st.levels.get(&key).copied().unwrap_or_default();
        let level = next_level(prev, max, warning, critical);
        if level != prev {
            st.levels.insert(key, level);
            if let Err(e) = ctx.outbox.save_level(key.dts_ch, key.dts_code, level.to_i32()).await {
                eprintln!("[outbox] gagal menyimpan level alarm: {e}");
            }
            let (event_type, lvl, threshold) = match level {
                Level::Normal => (AlarmEventType::Cleared, None, None),
                Level::Warning => (AlarmEventType::Triggered, Some(SegmentStatus::Warning), Some(warning)),
                Level::Critical => (AlarmEventType::Triggered, Some(SegmentStatus::Critical), Some(critical)),
            };
            let ev = IngestAlarm {
                event_id: Uuid::new_v4().to_string(),
                key,
                event_type,
                level: lvl,
                temperature: Some(max),
                threshold,
                occurred_at: now,
            };
            enqueue_json(ctx, KIND_ALARM, &ev).await;
        }

        segments.push(LiveSegmentSample {
            key,
            temp_avg: avg,
            temp_min: min,
            temp_max: max,
            temp_min_p: l.temp_min_p,
            temp_max_p: l.temp_max_p,
            status: status_of(level),
        });
        samples.push((key, avg, min, max));
    }

    if let Some(rows) = st.agg.add(now, &samples) {
        if !rows.is_empty() {
            enqueue_json(ctx, KIND_HISTORY, &IngestHistory { rows }).await;
        }
    }

    check_acknowledgements(ctx, st, now).await;

    let points = load_points(ctx, &mappings).await;
    let payload = IngestLive { measured_at: now, segments, points };
    let body = serde_json::to_string(&payload).map_err(|x| x.to_string())?;
    let result = ctx.cloud.send(Method::POST, "/ingest/live", body).await;
    let ok = result.is_ok();
    if st.live_ok != Some(ok) {
        match &result {
            Ok(()) => println!("[live] terhubung ke cloud ({} segmen, {} titik)", payload.segments.len(), payload.points.len()),
            Err(SendError::Retry(w)) | Err(SendError::Drop(w)) => eprintln!("[live] gagal kirim: {w}"),
        }
        st.live_ok = Some(ok);
    }
    Ok(())
}

async fn sync_segments(ctx: &Ctx, st: &mut State, mappings: &[source::Mapping]) {
    let infos: Vec<SegmentInfo> = mappings
        .iter()
        .map(|m| SegmentInfo {
            key: SegmentKey { dts_ch: m.dts_ch, dts_code: m.dts_code },
            original_name: m.original_name.clone(),
            custom_name: m.custom_name.clone(),
            main_group: m.main_group.clone(),
            sub_group: m.sub_group.clone(),
            start_m: m.start_m,
            end_m: m.end_m,
        })
        .collect();
    let Ok(json) = serde_json::to_string(&IngestSegments { segments: infos }) else { return };
    let stale = st.segments_synced_at.map_or(true, |t| t.elapsed() >= SEGMENT_RESYNC);
    if json != st.segments_json || stale {
        if let Err(e) = ctx.outbox.enqueue(KIND_SEGMENTS, &json).await {
            eprintln!("[outbox] gagal menyimpan segmen: {e}");
            return;
        }
        st.segments_json = json;
        st.segments_synced_at = Some(Instant::now());
    }
}

/// Titik spasial per channel, dibatasi pada rentang meter yang dipakai mapping (seperti desktop).
async fn load_points(ctx: &Ctx, mappings: &[source::Mapping]) -> Vec<LivePointSample> {
    let mut bounds: HashMap<i32, (usize, usize)> = HashMap::new();
    for m in mappings {
        let (s, en) = (m.start_m.unwrap_or(0).max(0) as usize, m.end_m.unwrap_or(0).max(0) as usize);
        let b = bounds.entry(m.dts_ch).or_insert((s, en));
        b.0 = b.0.min(s);
        b.1 = b.1.max(en);
    }
    let curves = match source::curves(&ctx.mysql).await {
        Ok(c) => c,
        Err(err) => {
            eprintln!("[curvebuff] {err}");
            return vec![];
        }
    };
    let mut points = Vec::new();
    for (ch, (start, end)) in bounds {
        if let Some(raw) = curves.get(&ch) {
            points.extend(curve::parse_curve(ch, raw, start, end));
        }
    }
    points
}

/// Alarm DTS yang sebelumnya terbuka lalu di-reset (acknowledge di lokal) -> event ACKNOWLEDGED.
async fn check_acknowledgements(ctx: &Ctx, st: &mut State, now: chrono::DateTime<Utc>) {
    let after = match st.ack_max_id {
        Some(id) => id,
        None => match source::alarmlog_max_id(&ctx.mysql).await {
            Ok(id) => {
                st.ack_max_id = Some(id);
                // Alarm yang sudah terbuka saat agent start ikut dipantau.
                id.max(0)
            }
            Err(err) => {
                eprintln!("[alarmlog] {err}");
                return;
            }
        },
    };
    // Jendela baca harus mencakup alarm yang masih dipantau; kalau tidak, baris yang sudah
    // di-reset tidak lagi terambil dan acknowledge tidak akan terdeteksi.
    let after = st
        .ack_open
        .iter()
        .min()
        .map_or(after, |min_open| after.min(min_open - 1));
    let rows = match source::alarmlog(&ctx.mysql, after).await {
        Ok(r) => r,
        Err(err) => {
            eprintln!("[alarmlog] {err}");
            return;
        }
    };
    for r in rows {
        st.ack_max_id = Some(st.ack_max_id.unwrap_or(0).max(r.id));
        if !r.reset {
            st.ack_open.insert(r.id);
        } else if st.ack_open.remove(&r.id) {
            let ev = IngestAlarm {
                // Deterministik: kiriman ulang untuk alarm yang sama tidak menggandakan event.
                event_id: Uuid::new_v5(&Uuid::NAMESPACE_OID, format!("dts-ack-{}", r.id).as_bytes()).to_string(),
                key: SegmentKey { dts_ch: r.ch, dts_code: r.code },
                event_type: AlarmEventType::Acknowledged,
                level: None,
                temperature: None,
                threshold: None,
                occurred_at: now,
            };
            enqueue_json(ctx, KIND_ALARM, &ev).await;
        }
    }
}
