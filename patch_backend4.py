import re

with open('src-tauri/src/lib.rs', 'r') as f:
    code = f.read()

old_alarm = """let rows: Vec<AlarmRow> = if let Some(ref d) = date {
        sqlx::query_as("SELECT ID, CreationTime, Ch, Code, AlarmPoint, AlarmCode, AlarmTemp, AlarmResetTime FROM alarmlog WHERE DATE(CreationTime) = ? ORDER BY CreationTime DESC LIMIT 1000")
            .bind(d)
            .fetch_all(&mysql_pool)
    } else {
        sqlx::query_as("SELECT ID, CreationTime, Ch, Code, AlarmPoint, AlarmCode, AlarmTemp, AlarmResetTime FROM alarmlog ORDER BY CreationTime DESC LIMIT 50")
            .fetch_all(&mysql_pool)
    }"""

new_alarm = """let rows: Vec<AlarmRow> = if let Some(ref d) = date {
        sqlx::query_as("SELECT ID, CreationTime, Ch, Code, AlarmPoint, AlarmCode, AlarmTemp, AlarmResetTime FROM alarmlog WHERE DATE(CreationTime) = ? ORDER BY CreationTime DESC LIMIT 1000")
            .bind(d)
            .fetch_all(&mysql_pool).await.unwrap_or_default()
    } else {
        sqlx::query_as("SELECT ID, CreationTime, Ch, Code, AlarmPoint, AlarmCode, AlarmTemp, AlarmResetTime FROM alarmlog ORDER BY CreationTime DESC LIMIT 50")
            .fetch_all(&mysql_pool).await.unwrap_or_default()
    };"""

code = code.replace(old_alarm, new_alarm)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(code)

