//! Tipe bersama antara agent (site) dan api (cloud).
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

/// Format respons standar semua endpoint REST.
#[derive(Debug, Serialize, Deserialize)]
pub struct ApiResponse<T> {
    pub success: bool,
    pub message: String,
    pub data: T,
}

impl<T> ApiResponse<T> {
    pub fn ok(message: impl Into<String>, data: T) -> Self {
        Self { success: true, message: message.into(), data }
    }
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "UPPERCASE")]
pub enum SegmentStatus {
    Normal,
    Warning,
    Critical,
}

/// Suhu terkini satu segmen (GET /api/v1/temperatures/live).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LiveTemperature {
    pub segment_code: String,
    pub main_group: String,
    pub distance_m: Option<f64>,
    pub temperature: f32,
    pub status: SegmentStatus,
    pub last_updated: DateTime<Utc>,
}

// ---------------------------------------------------------------------------
// Kontrak ingest: agent (site) -> api (cloud). Semua suhu dalam derajat Celsius.
// Autentikasi: header "X-API-Key" (role agent).
// ---------------------------------------------------------------------------

/// Kunci segmen sebagaimana dikenal DTS.
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub struct SegmentKey {
    pub dts_ch: i32,
    pub dts_code: i32,
}

/// POST /api/v1/ingest/live  (tiap ~10 detik; juga berfungsi sebagai heartbeat)
#[derive(Debug, Serialize, Deserialize)]
pub struct IngestLive {
    pub measured_at: DateTime<Utc>,
    pub segments: Vec<LiveSegmentSample>,
    /// Profil spasial per titik sensor; None = tidak ada sensor.
    pub points: Vec<LivePointSample>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LiveSegmentSample {
    pub key: SegmentKey,
    pub temp_avg: f32,
    pub temp_min: f32,
    pub temp_max: f32,
    pub temp_min_p: Option<i32>,
    pub temp_max_p: Option<i32>,
    pub status: SegmentStatus,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LivePointSample {
    pub dts_ch: i32,
    pub dts_code: i32,
    pub temp: Option<f32>,
}

/// POST /api/v1/ingest/history  (tiap 1 menit, batch; idempotent per segmen+menit)
#[derive(Debug, Serialize, Deserialize)]
pub struct IngestHistory {
    pub rows: Vec<HistoryRow>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct HistoryRow {
    pub key: SegmentKey,
    /// Awal menit (dibulatkan ke :00 detik).
    pub ts: DateTime<Utc>,
    pub temp_avg: f32,
    pub temp_min: f32,
    pub temp_max: f32,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "UPPERCASE")]
pub enum AlarmEventType {
    Triggered,
    Cleared,
    /// Acknowledge hanya dilakukan di lokal; cloud hanya menerima statusnya.
    Acknowledged,
}

/// POST /api/v1/ingest/alarm  (langsung saat terjadi, prioritas di antrean agent)
#[derive(Debug, Serialize, Deserialize)]
pub struct IngestAlarm {
    /// UUID dibuat di site; kiriman ulang diabaikan cloud (idempotent).
    pub event_id: String,
    pub key: SegmentKey,
    pub event_type: AlarmEventType,
    pub level: Option<SegmentStatus>,
    pub temperature: Option<f32>,
    pub threshold: Option<f32>,
    pub occurred_at: DateTime<Utc>,
}

/// PUT /api/v1/ingest/segments  (saat start agent, saat konfigurasi berubah, dan sinkron penuh berkala)
#[derive(Debug, Serialize, Deserialize)]
pub struct IngestSegments {
    pub segments: Vec<SegmentInfo>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SegmentInfo {
    pub key: SegmentKey,
    pub original_name: String,
    pub custom_name: Option<String>,
    pub main_group: String,
    pub sub_group: Option<String>,
    pub start_m: Option<i32>,
    pub end_m: Option<i32>,
}
