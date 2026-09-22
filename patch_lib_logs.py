import re

with open('src-tauri/src/lib.rs', 'r') as f:
    content = f.read()

log_commands = """
#[derive(serde::Serialize)]
pub struct SystemLog {
    pub id: i32,
    pub timestamp: String,
    pub event_type: String,
    pub message: String,
}

#[tauri::command]
async fn write_system_log(event_type: String, message: String, state: tauri::State<'_, SqlitePool>) -> Result<(), String> {
    sqlx::query("INSERT INTO system_logs (event_type, message) VALUES (?, ?)")
        .bind(&event_type)
        .bind(&message)
        .execute(&*state)
        .await
        .map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
async fn get_system_logs(state: tauri::State<'_, SqlitePool>) -> Result<Vec<SystemLog>, String> {
    let rows: Vec<(i32, String, String, String)> = sqlx::query_as(
        "SELECT id, datetime(timestamp, 'localtime'), event_type, message FROM system_logs ORDER BY id DESC LIMIT 500"
    )
    .fetch_all(&*state)
    .await
    .map_err(|e| e.to_string())?;
    
    let logs = rows.into_iter().map(|(id, timestamp, event_type, message)| SystemLog {
        id, timestamp, event_type, message
    }).collect();
    
    Ok(logs)
}
"""

if "write_system_log" not in content:
    content = content.replace("#[tauri::command]\nasync fn save_setting", log_commands + "\n#[tauri::command]\nasync fn save_setting")
    
    # Also add to invoke_handler
    content = content.replace("generate_pdf_report,", "generate_pdf_report,\n            write_system_log,\n            get_system_logs,")

# Also inject a log into save_setting
if "write_system_log" in log_commands:
    # Inside save_setting:
    save_old = """    sqlx::query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)")
        .bind(&key)
        .bind(&value)
        .execute(&*state)
        .await
        .map_err(|e| e.to_string())?;
"""
    save_new = save_old + """
    if key == "warning_threshold" || key == "critical_threshold" {
        let _ = sqlx::query("INSERT INTO system_logs (event_type, message) VALUES ('CONFIG', ?)")
            .bind(format!("Parameter {} diubah menjadi {}", key, value))
            .execute(&*state).await;
    }
"""
    content = content.replace(save_old, save_new)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(content)

