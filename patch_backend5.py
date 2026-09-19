import re

with open('src-tauri/src/lib.rs', 'r') as f:
    code = f.read()

old_get_groups_history = """async fn get_groups_history(
    minutes: i32,
    state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<GroupHistoryPoint>, String> {"""

new_get_groups_history = """async fn get_groups_history(
    minutes: i32,
    date: Option<String>,
    state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<GroupHistoryPoint>, String> {"""

code = code.replace(old_get_groups_history, new_get_groups_history)

old_query = """let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
            .bind(map.dts_ch).bind(map.dts_code).bind(limit)
            .fetch_all(&mysql_pool)
            .await.unwrap_or_default();"""

new_query = """let rows: Vec<HistRow> = if let Some(ref d) = date {
            sqlx::query_as("SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? AND DATE(CreationTime) = ? ORDER BY CreationTime DESC LIMIT ?")
                .bind(map.dts_ch).bind(map.dts_code).bind(d).bind(limit)
                .fetch_all(&mysql_pool)
                .await.unwrap_or_default()
        } else {
            sqlx::query_as("SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
                .bind(map.dts_ch).bind(map.dts_code).bind(limit)
                .fetch_all(&mysql_pool)
                .await.unwrap_or_default()
        };"""

code = code.replace(old_query, new_query)

old_get_alarms = """async fn get_alarms(state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>) -> Result<Vec<AlarmLog>, String> {"""
new_get_alarms = """async fn get_alarms(date: Option<String>, state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>) -> Result<Vec<AlarmLog>, String> {"""

code = code.replace(old_get_alarms, new_get_alarms)

old_alarm_query = """let rows: Vec<AlarmRow> = sqlx::query_as("SELECT ID, CreationTime, Ch, Code, AlarmPoint, AlarmCode, AlarmTemp, AlarmResetTime FROM alarmlog ORDER BY CreationTime DESC LIMIT 50")
        .fetch_all(&mysql_pool)
        .await.map_err(|e| e.to_string())?;"""

new_alarm_query = """let rows: Vec<AlarmRow> = if let Some(ref d) = date {
        sqlx::query_as("SELECT ID, CreationTime, Ch, Code, AlarmPoint, AlarmCode, AlarmTemp, AlarmResetTime FROM alarmlog WHERE DATE(CreationTime) = ? ORDER BY CreationTime DESC LIMIT 1000")
            .bind(d)
            .fetch_all(&mysql_pool).await.map_err(|e| e.to_string())?
    } else {
        sqlx::query_as("SELECT ID, CreationTime, Ch, Code, AlarmPoint, AlarmCode, AlarmTemp, AlarmResetTime FROM alarmlog ORDER BY CreationTime DESC LIMIT 50")
            .fetch_all(&mysql_pool).await.map_err(|e| e.to_string())?
    };"""

code = code.replace(old_alarm_query, new_alarm_query)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(code)

