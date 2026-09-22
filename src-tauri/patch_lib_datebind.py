import re

with open('src/lib.rs', 'r') as f:
    content = f.read()

# Replace get_groups_history
groups_old = """async fn get_groups_history(
    start_dt: String,
    end_dt: String,
    state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<GroupHistoryPoint>, String> {"""

groups_new = """async fn get_groups_history(
    start_dt: String,
    end_dt: String,
    state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<GroupHistoryPoint>, String> {
    use chrono::{Local, TimeZone, NaiveDateTime};
    let parsed_start = Local.from_local_datetime(&NaiveDateTime::parse_from_str(&start_dt, "%Y-%m-%d %H:%M:%S").map_err(|e| e.to_string())?).unwrap();
    let parsed_end = Local.from_local_datetime(&NaiveDateTime::parse_from_str(&end_dt, "%Y-%m-%d %H:%M:%S").map_err(|e| e.to_string())?).unwrap();"""
content = content.replace(groups_old, groups_new)

content = content.replace(
    ".bind(map.dts_ch).bind(map.dts_code).bind(&start_dt).bind(&end_dt).bind(limit)",
    ".bind(map.dts_ch).bind(map.dts_code).bind(parsed_start).bind(parsed_end).bind(limit)"
)

with open('src/lib.rs', 'w') as f:
    f.write(content)

