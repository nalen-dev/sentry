use chrono::NaiveDateTime;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct AlarmLog {
    #[sqlx(rename = "ID")]
    pub id: i32,
    #[sqlx(rename = "CreationTime")]
    pub creation_time: Option<NaiveDateTime>,
    #[sqlx(rename = "Ch")]
    pub ch: Option<i32>,
    #[sqlx(rename = "Code")]
    pub code: Option<i32>,
    #[sqlx(rename = "Name")]
    pub name: Option<String>,
    #[sqlx(rename = "AlarmPoint")]
    pub alarm_point: Option<i32>,
    #[sqlx(rename = "AlarmCode")]
    pub alarm_code: Option<i32>,
    #[sqlx(rename = "AlarmTemp")]
    pub alarm_temp: Option<i32>,
    #[sqlx(rename = "AlarmResetTime")]
    pub alarm_reset_time: Option<NaiveDateTime>,
    #[sqlx(rename = "Operator")]
    pub operator: Option<String>,
    #[sqlx(rename = "Flag")]
    pub flag: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct ChInfo {
    #[sqlx(rename = "ID")]
    pub id: i32,
    #[sqlx(rename = "Code")]
    pub code: Option<i32>,
    #[sqlx(rename = "En")]
    pub en: Option<i32>,
    #[sqlx(rename = "Length")]
    pub length: Option<i32>,
    #[sqlx(rename = "LengthReal")]
    pub length_real: Option<i32>,
    #[sqlx(rename = "CutFiberSt")]
    pub cut_fiber_st: Option<i32>,
    #[sqlx(rename = "LenRatio")]
    pub len_ratio: Option<f32>,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct Config {
    pub id: i32,
    #[sqlx(rename = "Ready")]
    pub ready: i32,
    #[sqlx(rename = "TempAlarmHighEn")]
    pub temp_alarm_high_en: i32,
    #[sqlx(rename = "TempAlarmLowEn")]
    pub temp_alarm_low_en: i32,
    #[sqlx(rename = "TempAlarmSpEn")]
    pub temp_alarm_sp_en: i32,
    #[sqlx(rename = "TempAlarmHighValue")]
    pub temp_alarm_high_value: i32,
    #[sqlx(rename = "TempAlarmLowValue")]
    pub temp_alarm_low_value: i32,
    #[sqlx(rename = "TempAlarmSpValue")]
    pub temp_alarm_sp_value: i32,
    #[sqlx(rename = "AlarmTimeValue")]
    pub alarm_time_value: i32,
    #[sqlx(rename = "AlarmBeepEn")]
    pub alarm_beep_en: i32,
    #[sqlx(rename = "Sensitivity")]
    pub sensitivity: i32,
    #[sqlx(rename = "TempAlarmIntervalEn")]
    pub temp_alarm_interval_en: Option<i32>,
    #[sqlx(rename = "TempUpLimitValue")]
    pub temp_up_limit_value: Option<i32>,
    #[sqlx(rename = "TempDownLimitValue")]
    pub temp_down_limit_value: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct CurveBuff {
    pub id: i32,
    #[sqlx(rename = "Ch")]
    pub ch: Option<i32>,
    #[sqlx(rename = "Buff")]
    pub buff: Option<Vec<u8>>,
    pub str: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct Device {
    #[sqlx(rename = "ID")]
    pub id: i32,
    #[sqlx(rename = "IP")]
    pub ip: Option<String>,
    #[sqlx(rename = "DevName")]
    pub dev_name: Option<String>,
    #[sqlx(rename = "DfbCurrent")]
    pub dfb_current: Option<i32>,
    #[sqlx(rename = "DfbTemp")]
    pub dfb_temp: Option<i32>,
    #[sqlx(rename = "DfbStatus")]
    pub dfb_status: Option<i32>,
    #[sqlx(rename = "PumpCurrent")]
    pub pump_current: Option<i32>,
    #[sqlx(rename = "PumpStatus")]
    pub pump_status: Option<i32>,
    #[sqlx(rename = "ApdStatus")]
    pub apd_status: Option<i32>,
    #[sqlx(rename = "TempModule")]
    pub temp_module: Option<i32>,
    #[sqlx(rename = "TempCase")]
    pub temp_case: Option<i32>,
    #[sqlx(rename = "LinkSt")]
    pub link_st: Option<i32>,
    #[sqlx(rename = "UpdateTime")]
    pub update_time: Option<NaiveDateTime>,
    #[sqlx(rename = "BcfStatus")]
    pub bcf_status: Option<i32>,
    #[sqlx(rename = "ExBcfStatus")]
    pub ex_bcf_status: Option<i32>,
    #[sqlx(rename = "ExReset")]
    pub ex_reset: Option<i32>,
    #[sqlx(rename = "FcAlarm")]
    pub fc_alarm: Option<i32>,
    #[sqlx(rename = "RecordInterval")]
    pub record_interval: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct FqHistoryList {
    pub id: i32,
    #[sqlx(rename = "CreationTime")]
    pub creation_time: Option<NaiveDateTime>,
    #[sqlx(rename = "Ch")]
    pub ch: i32,
    #[sqlx(rename = "Code")]
    pub code: i32,
    #[sqlx(rename = "TempAvg")]
    pub temp_avg: i32,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct OptFqList {
    #[sqlx(rename = "ID")]
    pub id: i32,
    #[sqlx(rename = "Ch")]
    pub ch: i32,
    #[sqlx(rename = "Code")]
    pub code: Option<i32>,
    #[sqlx(rename = "FqTable")]
    pub fq_table: Option<String>,
    #[sqlx(rename = "Start")]
    pub start: Option<i32>,
    #[sqlx(rename = "End")]
    pub end: Option<i32>,
    #[sqlx(rename = "Lenght")]
    pub lenght: Option<i32>,
    #[sqlx(rename = "Status")]
    pub status: Option<i32>,
    #[sqlx(rename = "TempMax")]
    pub temp_max: Option<i32>,
    #[sqlx(rename = "TempMin")]
    pub temp_min: Option<i32>,
    #[sqlx(rename = "TempAvg")]
    pub temp_avg: Option<i32>,
    #[sqlx(rename = "TempMaxP")]
    pub temp_max_p: Option<i32>,
    #[sqlx(rename = "TempMinP")]
    pub temp_min_p: Option<i32>,
    #[sqlx(rename = "AlarmValue")]
    pub alarm_value: Option<i32>,
    #[sqlx(rename = "Link")]
    pub link: Option<i32>,
    #[sqlx(rename = "Relay")]
    pub relay: Option<i32>,
    #[sqlx(rename = "Cutoff")]
    pub cutoff: Option<i32>,
    #[sqlx(rename = "AlarmType")]
    pub alarm_type: Option<i32>,
    #[sqlx(rename = "AlarmStatus")]
    pub alarm_status: Option<i32>,
    #[sqlx(rename = "Bypass")]
    pub bypass: Option<i32>,
    #[sqlx(rename = "Remark")]
    pub remark: Option<String>,
    #[sqlx(rename = "StartX")]
    pub start_x: Option<i32>,
    #[sqlx(rename = "StartY")]
    pub start_y: Option<i32>,
    #[sqlx(rename = "EndX")]
    pub end_x: Option<i32>,
    #[sqlx(rename = "EndY")]
    pub end_y: Option<i32>,
    #[sqlx(rename = "Mark")]
    pub mark: Option<i32>,
    #[sqlx(rename = "StartX2")]
    pub start_x2: Option<i32>,
    #[sqlx(rename = "StartY2")]
    pub start_y2: Option<i32>,
    #[sqlx(rename = "EndX2")]
    pub end_x2: Option<i32>,
    #[sqlx(rename = "EndY2")]
    pub end_y2: Option<i32>,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct DtsUser {
    pub id: i32,
    #[sqlx(rename = "Uid")]
    pub uid: Option<i32>,
    #[sqlx(rename = "Name")]
    pub name: Option<String>,
    #[sqlx(rename = "Password")]
    pub password: Option<String>,
    #[sqlx(rename = "Type")]
    pub user_type: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct UserLog {
    #[sqlx(rename = "ID")]
    pub id: i32,
    #[sqlx(rename = "CreationTime")]
    pub creation_time: Option<NaiveDateTime>,
    #[sqlx(rename = "Event")]
    pub event: Option<String>,
    #[sqlx(rename = "UserID")]
    pub user_id: Option<i32>,
    #[sqlx(rename = "Remark")]
    pub remark: Option<String>,
}
