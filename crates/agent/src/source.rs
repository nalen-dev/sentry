//! Pembacaan sumber data lokal: SQLite aplikasi desktop (mapping, threshold, setting DB)
//! dan MySQL unit DTS (suhu live, kurva per titik, alarmlog). Semua bersifat read-only.

use std::{collections::HashMap, path::Path, str::FromStr};

use sqlx::{
    mysql::MySqlConnectOptions,
    sqlite::{SqliteConnectOptions, SqlitePoolOptions},
    MySqlPool, SqlitePool,
};

use crate::config::MysqlOverride;

pub struct Mapping {
    pub dts_ch: i32,
    pub dts_code: i32,
    pub original_name: String,
    pub custom_name: Option<String>,
    pub main_group: String,
    pub sub_group: Option<String>,
    pub start_m: Option<i32>,
    pub end_m: Option<i32>,
}

pub struct LiveRow {
    pub ch: i32,
    pub code: i32,
    pub temp_avg: Option<i32>,
    pub temp_min: Option<i32>,
    pub temp_max: Option<i32>,
    pub temp_min_p: Option<i32>,
    pub temp_max_p: Option<i32>,
}

pub struct AlarmLogRow {
    pub id: i32,
    pub ch: i32,
    pub code: i32,
    pub reset: bool,
}

pub async fn open_sqlite(path: &Path) -> Result<SqlitePool, sqlx::Error> {
    // Hanya membaca; aplikasi desktop tetap satu-satunya penulis.
    let opts = SqliteConnectOptions::new().filename(path).read_only(true);
    SqlitePoolOptions::new().max_connections(2).connect_with(opts).await
}

async fn settings(pool: &SqlitePool) -> Result<HashMap<String, String>, sqlx::Error> {
    let rows: Vec<(String, String)> = sqlx::query_as("SELECT key, value FROM settings").fetch_all(pool).await?;
    Ok(rows.into_iter().collect())
}

/// Opsi koneksi MySQL: env menimpa, selain itu db_* dari tabel settings desktop.
pub async fn mysql_options(pool: &SqlitePool, ov: &MysqlOverride) -> Result<MySqlConnectOptions, String> {
    let s = settings(pool).await.map_err(|e| e.to_string())?;
    let pick = |ovr: &Option<String>, key: &str| ovr.clone().or_else(|| s.get(key).cloned());
    let host = pick(&ov.host, "db_host").ok_or("db_host belum ada di settings (atau set DTS_MYSQL_HOST)")?;
    let user = pick(&ov.user, "db_user").ok_or("db_user belum ada di settings (atau set DTS_MYSQL_USER)")?;
    let pass = pick(&ov.pass, "db_pass").ok_or("db_pass belum ada di settings (atau set DTS_MYSQL_PASS)")?;
    let name = pick(&ov.name, "db_name").ok_or("db_name belum ada di settings (atau set DTS_MYSQL_NAME)")?;
    let port = pick(&ov.port, "db_port").and_then(|p| p.parse().ok()).unwrap_or(3306);
    Ok(MySqlConnectOptions::new().host(&host).port(port).username(&user).password(&pass).database(&name))
}

/// Threshold dibaca ulang tiap siklus, jadi perubahan di desktop langsung berlaku.
pub async fn thresholds(pool: &SqlitePool) -> Result<(f32, f32), sqlx::Error> {
    let s = settings(pool).await?;
    let get = |k: &str, d: f32| s.get(k).and_then(|v| f32::from_str(v).ok()).unwrap_or(d);
    Ok((get("warning_threshold", 60.0), get("critical_threshold", 70.0)))
}

pub async fn mappings(pool: &SqlitePool) -> Result<Vec<Mapping>, sqlx::Error> {
    #[allow(clippy::type_complexity)]
    let rows: Vec<(i32, i32, String, Option<String>, String, Option<String>, Option<i32>, Option<i32>)> =
        sqlx::query_as(
            "SELECT dts_ch, dts_code, original_name, custom_name, main_group, sub_group, start_m, end_m
             FROM segment_mappings ORDER BY dts_ch, dts_code",
        )
        .fetch_all(pool)
        .await?;
    Ok(rows
        .into_iter()
        .map(|(dts_ch, dts_code, original_name, custom_name, main_group, sub_group, start_m, end_m)| Mapping {
            dts_ch, dts_code, original_name, custom_name, main_group, sub_group, start_m, end_m,
        })
        .collect())
}

pub async fn live(my: &MySqlPool) -> Result<Vec<LiveRow>, sqlx::Error> {
    let rows: Vec<(i32, Option<i32>, Option<i32>, Option<i32>, Option<i32>, Option<i32>, Option<i32>)> =
        sqlx::query_as("SELECT Ch, Code, TempAvg, TempMin, TempMax, TempMinP, TempMaxP FROM opt_fq_list")
            .fetch_all(my)
            .await?;
    Ok(rows
        .into_iter()
        .filter_map(|(ch, code, a, mn, mx, mnp, mxp)| {
            Some(LiveRow { ch, code: code?, temp_avg: a, temp_min: mn, temp_max: mx, temp_min_p: mnp, temp_max_p: mxp })
        })
        .collect())
}

/// Ch -> string kurva mentah.
pub async fn curves(my: &MySqlPool) -> Result<HashMap<i32, String>, sqlx::Error> {
    let rows: Vec<(i32, Option<String>)> = sqlx::query_as("SELECT Ch, str FROM curvebuff").fetch_all(my).await?;
    Ok(rows.into_iter().filter_map(|(ch, s)| s.map(|s| (ch, s))).collect())
}

pub async fn alarmlog_max_id(my: &MySqlPool) -> Result<i32, sqlx::Error> {
    let (id,): (i32,) = sqlx::query_as("SELECT CAST(COALESCE(MAX(ID), 0) AS SIGNED) FROM alarmlog").fetch_one(my).await?;
    Ok(id)
}

/// Baris baru (ID > after) ditambah semua baris yang masih terbuka (belum di-reset).
pub async fn alarmlog(my: &MySqlPool, after: i32) -> Result<Vec<AlarmLogRow>, sqlx::Error> {
    let rows: Vec<(i32, Option<i32>, Option<i32>, i64)> = sqlx::query_as(
        "SELECT ID, Ch, Code, CAST(AlarmResetTime IS NOT NULL AS SIGNED)
         FROM alarmlog WHERE ID > ? OR AlarmResetTime IS NULL",
    )
    .bind(after)
    .fetch_all(my)
    .await?;
    Ok(rows
        .into_iter()
        .map(|(id, ch, code, reset)| AlarmLogRow { id, ch: ch.unwrap_or(0), code: code.unwrap_or(0), reset: reset != 0 })
        .collect())
}
