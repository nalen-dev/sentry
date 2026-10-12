use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct AppUser {
    pub id: String,
    pub role: String,
    pub status: String,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct AppSetting {
    pub key: String,
    pub value: String,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct SegmentMapping {
    pub id: Option<i32>,
    pub dts_ch: i32,
    pub dts_code: i32,
    pub original_name: String,
    pub custom_name: Option<String>,
    pub main_group: String,
    pub sub_group: Option<String>,
    pub start_m: Option<i32>,
    pub end_m: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct MapCalibration {
    pub id: Option<i32>,
    pub main_group: String,
    pub start_m: i32,
    pub end_m: i32,
    pub start_svg_x: f32,
    pub start_svg_y: f32,
    pub end_svg_x: f32,
    pub end_svg_y: f32,
    pub start_lat: Option<f32>,
    pub start_lng: Option<f32>,
    pub end_lat: Option<f32>,
    pub end_lng: Option<f32>,
}
