import re

with open('src/lib.rs', 'r') as f:
    content = f.read()

# Add imports and MysqlState struct
imports = """use tokio::sync::Mutex;
use sqlx::mysql::{MySqlPool, MySqlPoolOptions, MySqlConnectOptions};

struct MysqlState(Mutex<Option<MySqlPool>>);
"""
content = re.sub(r'(use serde::\{Serialize, Deserialize\};)', r'\1\n' + imports, content)

# Modify save_setting
save_setting_new = """#[tauri::command]
async fn save_setting(key: String, value: String, state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>) -> Result<(), String> {
    sqlx::query("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value")
        .bind(&key)
        .bind(value)
        .execute(&*state)
        .await
        .map_err(|e| e.to_string())?;
        
    if key.starts_with("db_") {
        let mut guard = mysql_state.0.lock().await;
        if let Some(pool) = guard.take() {
            pool.close().await;
        }
    }
    
    Ok(())
}

async fn get_mysql_pool(sqlite_pool: &SqlitePool, mysql_state: &tauri::State<'_, MysqlState>) -> Result<MySqlPool, String> {
    let mut guard = mysql_state.0.lock().await;
    if let Some(pool) = &*guard {
        return Ok(pool.clone());
    }

    let rows: Vec<(String, String)> = sqlx::query_as("SELECT key, value FROM settings").fetch_all(sqlite_pool).await.map_err(|e| e.to_string())?;
    let mut settings = std::collections::HashMap::new();
    for (k, v) in rows { settings.insert(k, v); }

    let db_host = settings.get("db_host").cloned().unwrap_or_else(|| "192.168.1.64".to_string());
    let db_port = settings.get("db_port").cloned().unwrap_or_else(|| "58329".to_string());
    let db_user = settings.get("db_user").cloned().unwrap_or_else(|| "root".to_string());
    let db_pass = settings.get("db_pass").cloned().unwrap_or_else(|| "l0mY4cH9H?h9".to_string());
    let db_name = settings.get("db_name").cloned().unwrap_or_else(|| "dtscontroler".to_string());
    
    let options = MySqlConnectOptions::new()
        .host(&db_host).port(db_port.parse().unwrap_or(3306)).username(&db_user).password(&db_pass).database(&db_name);
        
    let pool = MySqlPoolOptions::new()
        .max_connections(10)
        .acquire_timeout(std::time::Duration::from_secs(5))
        .connect_with(options).await.map_err(|e| format!("MySQL Connection Failed: {}", e))?;
        
    *guard = Some(pool.clone());
    Ok(pool.clone())
}
"""

content = re.sub(r'#\[tauri::command\]\nasync fn save_setting.*?Ok\(\(\)\)\n\}', save_setting_new, content, flags=re.DOTALL)

# Replace all occurrences of mysql pool creation in the queries with get_mysql_pool

def replace_db_fetch(func_name, content):
    pattern = r'#\[tauri::command\]\nasync fn ' + func_name + r'\((.*?)\).*?\{.*?let mut db_host.*?\n.*?let mysql_pool = .*?\n'
    # wait, the pattern is tricky. I'll replace the whole block that fetches settings and creates pool.
    block_pattern = r'let rows: Vec<\(String, String\)> = sqlx::query_as\("SELECT key, value FROM settings"\)\s*\.fetch_all\(&\*state\)\.await\.[^;]*;\s*let mut settings = HashMap::new\(\);\s*for \(k, v\) in rows \{ settings\.insert\(k, v\); \}\s*let mut db_host.*?;.*?let mysql_pool = sqlx::mysql::MySqlPoolOptions::new\(\).*?;'
    
    replacement = r'let mysql_pool = get_mysql_pool(&state, &mysql_state).await?;'
    return re.sub(block_pattern, replacement, content, flags=re.DOTALL)

def replace_db_fetch_2(content):
    block_pattern = r'let rows: Vec<\(String, String\)> = sqlx::query_as\("SELECT key, value FROM settings"\)\s*\.fetch_all\(&\*state\)\.await\.[^;]*;\s*let mut db_host.*?;.*?let mysql_pool = sqlx::mysql::MySqlPoolOptions::new\(\).*?;'
    replacement = r'let mysql_pool = get_mysql_pool(&state, &mysql_state).await?;'
    return re.sub(block_pattern, replacement, content, flags=re.DOTALL)

content = replace_db_fetch('sync_dts_segments', content)
content = replace_db_fetch('get_live_segments', content)
content = replace_db_fetch('get_segment_curve', content)
content = replace_db_fetch('get_segment_history', content)
content = replace_db_fetch('get_alarms', content)
content = replace_db_fetch_2(content)

# We need to add mysql_state: tauri::State<'_, MysqlState> to the parameters of those functions
for func in ['sync_dts_segments', 'get_live_segments', 'get_segment_curve', 'get_segment_history', 'get_alarms']:
    content = re.sub(r'(async fn ' + func + r'\([^)]*state: tauri::State<\'_, SqlitePool>)(\s*\))', r'\1, mysql_state: tauri::State<\'_, MysqlState>\2', content)

# In the setup phase we need to add the state
setup_new = r"""handle.manage(pool);
                handle.manage(MysqlState(Mutex::new(None)));"""
content = content.replace("handle.manage(pool);", setup_new)

with open('src/lib.rs', 'w') as f:
    f.write(content)

