import re

with open('src-tauri/src/lib.rs', 'r') as f:
    code = f.read()

# Add ack_all_alarms
ack_command = """
#[tauri::command]
async fn ack_all_alarms(state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>) -> Result<(), String> {
    let mysql_pool = get_mysql_pool(&state, &mysql_state).await?;
    sqlx::query("UPDATE alarmlog SET AlarmResetTime = NOW() WHERE AlarmResetTime IS NULL")
        .execute(&mysql_pool)
        .await
        .map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
async fn test_db_connection("""

code = code.replace("#[tauri::command]\nasync fn test_db_connection(", ack_command)

# Add to invoke handler
code = code.replace("get_alarms,", "get_alarms, ack_all_alarms,")

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(code)

