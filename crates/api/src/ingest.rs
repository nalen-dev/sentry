use axum::{extract::State, http::HeaderMap, Json};
use chrono::{DateTime, NaiveDate, Utc};
use dts_shared::{
    ApiResponse, IngestAlarm, IngestHistory, IngestLive, IngestSegments, SegmentStatus,
};

use crate::{auth::authenticate, error::AppError, AppState};

type Resp = Result<Json<ApiResponse<serde_json::Value>>, AppError>;

fn ok(msg: &str, n: usize) -> Resp {
    Ok(Json(ApiResponse::ok(msg, serde_json::json!({ "accepted": n }))))
}

pub fn status_str(s: SegmentStatus) -> &'static str {
    match s {
        SegmentStatus::Normal => "NORMAL",
        SegmentStatus::Warning => "WARNING",
        SegmentStatus::Critical => "CRITICAL",
    }
}

async fn agent_site(state: &AppState, headers: &HeaderMap) -> Result<i16, AppError> {
    authenticate(&state.pool, headers, "agent")
        .await?
        .site_id
        .ok_or_else(AppError::forbidden)
}

/// PUT /ingest/segments: upsert master segmen.
pub async fn segments(
    State(st): State<AppState>,
    h: HeaderMap,
    Json(body): Json<IngestSegments>,
) -> Resp {
    let site = agent_site(&st, &h).await?;
    let n = body.segments.len();
    let mut tx = st.pool.begin().await?;
    for s in &body.segments {
        sqlx::query(
            "INSERT INTO segment (site_id, dts_ch, dts_code, original_name, custom_name, main_group, sub_group, start_m, end_m)
             VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
             ON CONFLICT (site_id, dts_ch, dts_code) DO UPDATE SET
               original_name = EXCLUDED.original_name, custom_name = EXCLUDED.custom_name,
               main_group = EXCLUDED.main_group, sub_group = EXCLUDED.sub_group,
               start_m = EXCLUDED.start_m, end_m = EXCLUDED.end_m",
        )
        .bind(site)
        .bind(s.key.dts_ch)
        .bind(s.key.dts_code)
        .bind(&s.original_name)
        .bind(&s.custom_name)
        .bind(&s.main_group)
        .bind(&s.sub_group)
        .bind(s.start_m)
        .bind(s.end_m)
        .execute(&mut *tx)
        .await?;
    }
    tx.commit().await?;
    ok("Segments synced", n)
}

/// POST /ingest/live: upsert kondisi terkini + heartbeat.
pub async fn live(State(st): State<AppState>, h: HeaderMap, Json(b): Json<IngestLive>) -> Resp {
    let site = agent_site(&st, &h).await?;
    let mut tx = st.pool.begin().await?;

    let seg = &b.segments;
    sqlx::query(
        "INSERT INTO live_segment (segment_id, temp_avg, temp_min, temp_max, temp_min_p, temp_max_p, status, measured_at)
         SELECT s.id, u.avg, u.mn, u.mx, u.minp, u.maxp, u.status, $9
         FROM UNNEST($2::int[], $3::int[], $4::real[], $5::real[], $6::real[], $7::int[], $8::int[], $10::text[])
              AS u(ch, code, avg, mn, mx, minp, maxp, status)
         JOIN segment s ON s.site_id = $1 AND s.dts_ch = u.ch AND s.dts_code = u.code
         ON CONFLICT (segment_id) DO UPDATE SET
           temp_avg = EXCLUDED.temp_avg, temp_min = EXCLUDED.temp_min, temp_max = EXCLUDED.temp_max,
           temp_min_p = EXCLUDED.temp_min_p, temp_max_p = EXCLUDED.temp_max_p,
           status = EXCLUDED.status, measured_at = EXCLUDED.measured_at",
    )
    .bind(site)
    .bind(seg.iter().map(|s| s.key.dts_ch).collect::<Vec<_>>())
    .bind(seg.iter().map(|s| s.key.dts_code).collect::<Vec<_>>())
    .bind(seg.iter().map(|s| s.temp_avg).collect::<Vec<_>>())
    .bind(seg.iter().map(|s| s.temp_min).collect::<Vec<_>>())
    .bind(seg.iter().map(|s| s.temp_max).collect::<Vec<_>>())
    .bind(seg.iter().map(|s| s.temp_min_p).collect::<Vec<_>>())
    .bind(seg.iter().map(|s| s.temp_max_p).collect::<Vec<_>>())
    .bind(b.measured_at)
    .bind(seg.iter().map(|s| status_str(s.status).to_string()).collect::<Vec<_>>())
    .execute(&mut *tx)
    .await?;

    let pts = &b.points;
    sqlx::query(
        "INSERT INTO live_point (site_id, dts_ch, dts_code, temp, measured_at)
         SELECT $1, ch, code, t, $5 FROM UNNEST($2::int[], $3::int[], $4::real[]) AS u(ch, code, t)
         ON CONFLICT (site_id, dts_ch, dts_code) DO UPDATE SET temp = EXCLUDED.temp, measured_at = EXCLUDED.measured_at",
    )
    .bind(site)
    .bind(pts.iter().map(|p| p.dts_ch).collect::<Vec<_>>())
    .bind(pts.iter().map(|p| p.dts_code).collect::<Vec<_>>())
    .bind(pts.iter().map(|p| p.temp).collect::<Vec<Option<f32>>>())
    .bind(b.measured_at)
    .execute(&mut *tx)
    .await?;

    sqlx::query("UPDATE site SET last_seen = now() WHERE id = $1")
        .bind(site)
        .execute(&mut *tx)
        .await?;
    tx.commit().await?;
    ok("Live data accepted", seg.len())
}

/// POST /ingest/history: agregat 1 menit (idempotent per segmen+menit).
pub async fn history(State(st): State<AppState>, h: HeaderMap, Json(b): Json<IngestHistory>) -> Resp {
    let site = agent_site(&st, &h).await?;
    let rows = &b.rows;

    // Pastikan partisi untuk tiap hari (UTC) pada batch tersedia (mis. data backlog).
    let mut days: Vec<NaiveDate> = rows.iter().map(|r| r.ts.date_naive()).collect();
    days.sort();
    days.dedup();
    for d in days {
        sqlx::query("SELECT ensure_history_partition($1)")
            .bind(d)
            .execute(&st.pool)
            .await?;
    }

    sqlx::query(
        "INSERT INTO segment_history_1m (segment_id, ts, temp_avg, temp_min, temp_max)
         SELECT s.id, u.ts, u.avg, u.mn, u.mx
         FROM UNNEST($2::int[], $3::int[], $4::timestamptz[], $5::real[], $6::real[], $7::real[])
              AS u(ch, code, ts, avg, mn, mx)
         JOIN segment s ON s.site_id = $1 AND s.dts_ch = u.ch AND s.dts_code = u.code
         ON CONFLICT (segment_id, ts) DO UPDATE SET
           temp_avg = EXCLUDED.temp_avg, temp_min = EXCLUDED.temp_min, temp_max = EXCLUDED.temp_max",
    )
    .bind(site)
    .bind(rows.iter().map(|r| r.key.dts_ch).collect::<Vec<_>>())
    .bind(rows.iter().map(|r| r.key.dts_code).collect::<Vec<_>>())
    .bind(rows.iter().map(|r| r.ts).collect::<Vec<DateTime<Utc>>>())
    .bind(rows.iter().map(|r| r.temp_avg).collect::<Vec<_>>())
    .bind(rows.iter().map(|r| r.temp_min).collect::<Vec<_>>())
    .bind(rows.iter().map(|r| r.temp_max).collect::<Vec<_>>())
    .execute(&st.pool)
    .await?;
    ok("History accepted", rows.len())
}

/// POST /ingest/alarm: event alarm (idempotent via event_id).
pub async fn alarm(State(st): State<AppState>, h: HeaderMap, Json(a): Json<IngestAlarm>) -> Resp {
    let site = agent_site(&st, &h).await?;
    let event_id = uuid::Uuid::parse_str(&a.event_id).map_err(|_| {
        AppError(axum::http::StatusCode::BAD_REQUEST, "event_id harus UUID".into())
    })?;
    let etype = serde_json::to_value(a.event_type).unwrap();
    let level = a.level.map(status_str);
    let res = sqlx::query(
        "INSERT INTO alarm_event (site_id, event_id, segment_id, event_type, level, temperature, threshold, occurred_at)
         SELECT $1, $2, s.id, $3, $4, $5, $6, $7 FROM segment s
         WHERE s.site_id = $1 AND s.dts_ch = $8 AND s.dts_code = $9
         ON CONFLICT (site_id, event_id) DO NOTHING",
    )
    .bind(site)
    .bind(event_id)
    .bind(etype.as_str())
    .bind(level)
    .bind(a.temperature)
    .bind(a.threshold)
    .bind(a.occurred_at)
    .bind(a.key.dts_ch)
    .bind(a.key.dts_code)
    .execute(&st.pool)
    .await?;
    // 0 baris = duplikat (aman) atau segmen belum disinkronkan.
    ok("Alarm event accepted", res.rows_affected() as usize)
}
