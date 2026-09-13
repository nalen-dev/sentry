pub mod domain;
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

#[tauri::command]
async fn toggle_fullscreen(window: tauri::Window) -> Result<bool, String> {
    let is_fullscreen = window.is_fullscreen().unwrap_or(false);
    let new_state = !is_fullscreen;
    
    // Set fullscreen
    window.set_fullscreen(new_state).map_err(|e| e.to_string())?;
    
    // Explicitly toggle decorations (titlebar) for true kiosk mode
    // Hide decorations if fullscreen, show if not
    let _ = window.set_decorations(!new_state);
    
    Ok(new_state)
}

#[derive(serde::Serialize)]
struct SyncResult {
    total_found: i32,
    new_added: i32,
}

#[tauri::command]
async fn sync_dts_segments(state: tauri::State<'_, SqlitePool>) -> Result<SyncResult, String> {
    // 1. Get MySQL connection settings from SQLite
    let settings: Vec<(String, String)> = sqlx::query_as("SELECT key, value FROM settings WHERE key LIKE 'db_%'")
        .fetch_all(&*state)
        .await
        .map_err(|e| format!("Failed to read DB settings: {}", e))?;
    
    let mut db_host = String::from("192.168.1.64");
    let mut db_port = String::from("58329");
    let mut db_user = String::from("root");
    let mut db_pass = String::from("l0mY4cH9H?h9");
    let mut db_name = String::from("dtscontroler");

    for (k, v) in settings {
        match k.as_str() {
            "db_host" => db_host = v,
            "db_port" => db_port = v,
            "db_user" => db_user = v,
            "db_pass" => db_pass = v,
            "db_name" => db_name = v,
            _ => {}
        }
    }

    let port_num = db_port.parse::<u16>().unwrap_or(3306);
    let options = sqlx::mysql::MySqlConnectOptions::new()
        .host(&db_host)
        .port(port_num)
        .username(&db_user)
        .password(&db_pass)
        .database(&db_name);
    
    // 2. Connect to MySQL with short timeout (since WSL might fail)
    let mysql_pool = sqlx::mysql::MySqlPoolOptions::new()
        .max_connections(1)
        .acquire_timeout(std::time::Duration::from_secs(3))
        .connect_with(options)
        .await
        .map_err(|e| format!("MySQL Connection Failed: {}", e))?;

    // 3. Fetch from opt_fq_list
    #[derive(sqlx::FromRow)]
    struct OptRow { ch: i32, code: Option<i32>, fq_table: Option<String>, start: Option<i32>, end: Option<i32> }

    let rows: Vec<OptRow> = sqlx::query_as("SELECT Ch as ch, Code as code, FqTable as fq_table, Start as start, End as end FROM opt_fq_list")
        .fetch_all(&mysql_pool)
        .await
        .map_err(|e| format!("Failed to fetch segments: {}", e))?;

    // 4. Sync to SQLite
    let mut new_added = 0;
    for row in &rows {
        if let Some(code) = row.code {
            let original_name = row.fq_table.clone().unwrap_or_else(|| format!("CSection{}", code));
            
            // First update start/end for existing ones
            let _ = sqlx::query("UPDATE segment_mappings SET start_m = ?, end_m = ? WHERE dts_ch = ? AND dts_code = ?")
                .bind(row.start)
                .bind(row.end)
                .bind(row.ch)
                .bind(code)
                .execute(&*state)
                .await;

            let result = sqlx::query(
                "INSERT OR IGNORE INTO segment_mappings (dts_ch, dts_code, original_name, main_group, start_m, end_m) 
                 VALUES (?, ?, ?, 'Unassigned', ?, ?)"
            )
            .bind(row.ch)
            .bind(code)
            .bind(original_name)
            .bind(row.start)
            .bind(row.end)
            .execute(&*state)
            .await;

            if let Ok(res) = result {
                if res.rows_affected() > 0 {
                    new_added += 1;
                }
            }
        }
    }

    Ok(SyncResult {
        total_found: rows.len() as i32,
        new_added,
    })
}

#[tauri::command]
async fn get_segment_mappings(state: tauri::State<'_, SqlitePool>) -> Result<Vec<crate::domain::app_models::SegmentMapping>, String> {
    let rows: Vec<crate::domain::app_models::SegmentMapping> = sqlx::query_as("SELECT * FROM segment_mappings ORDER BY dts_ch, dts_code")
        .fetch_all(&*state)
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(rows)
}

#[tauri::command]
async fn update_segment_mapping(
    id: i32, 
    custom_name: Option<String>, 
    main_group: String, 
    sub_group: Option<String>,
    state: tauri::State<'_, SqlitePool>
) -> Result<(), String> {
    sqlx::query("UPDATE segment_mappings SET custom_name = ?, main_group = ?, sub_group = ? WHERE id = ?")
        .bind(custom_name)
        .bind(main_group)
        .bind(sub_group)
        .bind(id)
        .execute(&*state)
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(())
}

#[tauri::command]
async fn test_db_connection(
    host: String,
    port: String,
    user: String,
    pass: String,
    name: String,
) -> Result<String, String> {
    let port_num = port.parse::<u16>().unwrap_or(3306);
    let options = sqlx::mysql::MySqlConnectOptions::new()
        .host(&host)
        .port(port_num)
        .username(&user)
        .password(&pass)
        .database(&name);
    
    let pool = sqlx::mysql::MySqlPoolOptions::new()
        .max_connections(1)
        .acquire_timeout(std::time::Duration::from_secs(3))
        .connect_with(options)
        .await
        .map_err(|e| format!("MySQL Connection Failed: {}", e))?;
        
    // Simple ping query
    sqlx::query("SELECT 1")
        .execute(&pool)
        .await
        .map_err(|e| format!("Query Failed: {}", e))?;
        
    Ok("Connection successful!".to_string())
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
        .invoke_handler(tauri::generate_handler![
            get_all_settings, 
            save_setting, 
            get_users, 
            toggle_fullscreen,
            sync_dts_segments,
            get_segment_mappings,
            update_segment_mapping,
            test_db_connection
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
