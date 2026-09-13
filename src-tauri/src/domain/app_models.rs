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
