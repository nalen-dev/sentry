mod db;

use sqlx::SqlitePool;
use std::collections::HashMap;
use tauri::Manager;
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, sqlx::FromRow)]
pub struct User {
    id: String,
    role: String,
    status: String,
}

#[tauri::command]
async fn get_all_settings(state: tauri::State<'_, SqlitePool>) -> Result<HashMap<String, String>, String> {
    let rows: Vec<(String, String)> = sqlx::query_as("SELECT key, value FROM settings")
        .fetch_all(&*state)
        .await
        .map_err(|e| e.to_string())?;
    
    let mut map = HashMap::new();
    for (k, v) in rows {
        map.insert(k, v);
    }
    
    Ok(map)
}

#[tauri::command]
async fn save_setting(key: String, value: String, state: tauri::State<'_, SqlitePool>) -> Result<(), String> {
    sqlx::query("INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value")
        .bind(key)
        .bind(value)
        .execute(&*state)
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
async fn get_users(state: tauri::State<'_, SqlitePool>) -> Result<Vec<User>, String> {
    let rows: Vec<User> = sqlx::query_as("SELECT id, role, status FROM users")
        .fetch_all(&*state)
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(rows)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            let handle = app.handle().clone();
            
            tauri::async_runtime::block_on(async move {
                // Get the application data directory
                let app_dir = handle.path().app_data_dir().expect("Failed to get app data dir");
                
                // Initialize database
                let pool = db::init_db(&app_dir).await.expect("Failed to initialize database");
                
                // Store connection pool in Tauri state
                handle.manage(pool);
            });
            
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![get_all_settings, save_setting, get_users])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
