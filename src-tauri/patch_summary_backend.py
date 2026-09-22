import re

with open('src/lib.rs', 'r') as f:
    content = f.read()

# Add the new command
new_cmd = """
#[derive(serde::Serialize)]
pub struct HistorySummary {
    pub max_temp: f32,
    pub max_time: String,
    pub max_group: String,
    pub max_segment: String,
    pub min_temp: f32,
    pub min_time: String,
    pub min_group: String,
    pub min_segment: String,
}

#[tauri::command]
async fn get_history_summary(
    start_dt: String,
    end_dt: String,
    state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Option<HistorySummary>, String> {
    use chrono::{Local, TimeZone, NaiveDateTime};
    let parsed_start = Local.from_local_datetime(&NaiveDateTime::parse_from_str(&start_dt, "%Y-%m-%d %H:%M:%S").map_err(|e| e.to_string())?).unwrap();
    let parsed_end = Local.from_local_datetime(&NaiveDateTime::parse_from_str(&end_dt, "%Y-%m-%d %H:%M:%S").map_err(|e| e.to_string())?).unwrap();

    let mut mysql_pool = mysql_state.0.lock().await.clone();
    if mysql_pool.is_none() {
        let settings = crate::db::get_settings(&*state).await.unwrap_or_default();
        let mut db_host = String::from("192.168.1.64");
        let mut db_port = String::from("58329");
        let mut db_user = String::from("root");
        let mut db_pass = String::from("l0mY4cH9H?h9");
        let mut db_name = String::from("dtscontroler");
        for (k, v) in settings { match k.as_str() { "db_host" => db_host = v, "db_port" => db_port = v, "db_user" => db_user = v, "db_pass" => db_pass = v, "db_name" => db_name = v, _ => {} } }
        let options = sqlx::mysql::MySqlConnectOptions::new().host(&db_host).port(db_port.parse().unwrap_or(3306)).username(&db_user).password(&db_pass).database(&db_name);
        if let Ok(p) = sqlx::mysql::MySqlPoolOptions::new().connect_with(options).await {
            *mysql_state.0.lock().await = Some(p.clone());
            mysql_pool = Some(p);
        }
    }
    
    let mysql_pool = mysql_pool.ok_or("No database connection")?;

    #[derive(sqlx::FromRow, Clone)]
    #[allow(non_snake_case)]
    struct HistRow { CreationTime: Option<chrono::DateTime<chrono::Local>>, TempAvg: Option<i32>, Ch: i32, Code: i32 }

    // Fetch Max
    let max_row: Option<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE CreationTime >= ? AND CreationTime <= ? ORDER BY TempAvg DESC LIMIT 1")
        .bind(parsed_start).bind(parsed_end)
        .fetch_optional(&mysql_pool)
        .await.unwrap_or(None);

    // Fetch Min
    let min_row: Option<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE CreationTime >= ? AND CreationTime <= ? AND TempAvg >= 0 ORDER BY TempAvg ASC LIMIT 1")
        .bind(parsed_start).bind(parsed_end)
        .fetch_optional(&mysql_pool)
        .await.unwrap_or(None);

    if max_row.is_none() || min_row.is_none() {
        return Ok(None);
    }
    
    let max_row = max_row.unwrap();
    let min_row = min_row.unwrap();

    let mappings = crate::domain::app_models::get_segment_mappings(&*state).await.unwrap_or_default();
    
    let get_info = |ch: i32, code: i32| -> (String, String) {
        if let Some(m) = mappings.iter().find(|m| m.dts_ch == ch && m.dts_code == code) {
            let name = if let Some(c) = &m.custom_name { if c.is_empty() { m.original_name.clone() } else { c.clone() } } else { m.original_name.clone() };
            (m.main_group.clone(), name)
        } else {
            ("Unknown".into(), format!("Ch{} Code{}", ch, code))
        }
    };

    let (max_grp, max_seg) = get_info(max_row.Ch, max_row.Code);
    let (min_grp, min_seg) = get_info(min_row.Ch, min_row.Code);

    Ok(Some(HistorySummary {
        max_temp: max_row.TempAvg.unwrap_or(0) as f32 / 10.0,
        max_time: max_row.CreationTime.map(|c| c.format("%H:%M:%S").to_string()).unwrap_or_default(),
        max_group: max_grp,
        max_segment: max_seg,
        min_temp: min_row.TempAvg.unwrap_or(0) as f32 / 10.0,
        min_time: min_row.CreationTime.map(|c| c.format("%H:%M:%S").to_string()).unwrap_or_default(),
        min_group: min_grp,
        min_segment: min_seg,
    }))
}

#[tauri::command]"""

content = content.replace("#[tauri::command]", new_cmd, 1)

# Register command
content = content.replace("get_groups_history,", "get_groups_history,\n            get_history_summary,")

with open('src/lib.rs', 'w') as f:
    f.write(content)

