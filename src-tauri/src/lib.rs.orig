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

    let rows: Vec<OptRow> = sqlx::query_as(
        "SELECT f.Ch as ch, f.Code as code, f.FqTable as fq_table, f.Start as start, f.End as end 
         FROM opt_fq_list f 
         JOIN chinfo c ON f.Ch = c.Code 
         WHERE c.En = 1"
    )
    .fetch_all(&mysql_pool)
    .await
    .map_err(|e| format!("Failed to fetch segments: {}", e))?;

    // Wipe old data completely (replace)
    let _ = sqlx::query("DELETE FROM segment_mappings").execute(&*state).await;

    // 4. Sync to SQLite
    let mut new_added = 0;
    for row in &rows {
        if let Some(code) = row.code {
            let original_name = row.fq_table.clone().unwrap_or_else(|| format!("CSection{}", code));
            
            let result = sqlx::query(
                "INSERT INTO segment_mappings (dts_ch, dts_code, original_name, main_group, start_m, end_m) 
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
    let _ = sqlx::query("UPDATE segment_mappings SET custom_name = ?, main_group = ?, sub_group = ? WHERE id = ?")
        .bind(custom_name)
        .bind(main_group)
        .bind(sub_group)
        .bind(id)
        .execute(&*state)
        .await
        .map_err(|e| format!("Failed to update mapping: {}", e))?;
    Ok(())
}

#[derive(serde::Serialize)]
pub struct LiveSegment {
    pub id: i32,
    pub dts_ch: i32,
    pub dts_code: i32,
    pub original_name: String,
    pub custom_name: Option<String>,
    pub main_group: String,
    pub sub_group: Option<String>,
    pub start_m: Option<i32>,
    pub end_m: Option<i32>,
    pub temp_avg: f32,
    pub temp_min: f32,
    pub temp_max: f32,
    pub temp_min_p: i32,
    pub temp_max_p: i32,
}

#[tauri::command]
async fn get_live_segments(state: tauri::State<'_, SqlitePool>) -> Result<Vec<LiveSegment>, String> {
    // Get local mappings
    let mappings = get_segment_mappings(state.clone()).await?;
    
    // Connect to MySQL
    let settings: Vec<(String, String)> = sqlx::query_as("SELECT key, value FROM settings WHERE key LIKE 'db_%'")
        .fetch_all(&*state)
        .await
        .map_err(|e| e.to_string())?;
        
    let mut db_host = String::from("192.168.1.64");
    let mut db_port = String::from("58329");
    let mut db_user = String::from("root");
    let mut db_pass = String::from("l0mY4cH9H?h9");
    let mut db_name = String::from("dtscontroler");
    for (k, v) in settings { match k.as_str() { "db_host" => db_host = v, "db_port" => db_port = v, "db_user" => db_user = v, "db_pass" => db_pass = v, "db_name" => db_name = v, _ => {} } }
    
    let port_num = db_port.parse::<u16>().unwrap_or(3306);
    let options = sqlx::mysql::MySqlConnectOptions::new().host(&db_host).port(port_num).username(&db_user).password(&db_pass).database(&db_name);
    
    let mysql_pool = sqlx::mysql::MySqlPoolOptions::new().max_connections(1).acquire_timeout(std::time::Duration::from_secs(3)).connect_with(options).await.map_err(|e| format!("MySQL Connection Failed: {}", e))?;
    
    #[derive(sqlx::FromRow)]
    struct LiveRow { ch: i32, code: i32, temp_avg: Option<i32>, temp_min: Option<i32>, temp_max: Option<i32>, temp_min_p: Option<i32>, temp_max_p: Option<i32> }
    
    let live_data: Vec<LiveRow> = sqlx::query_as("SELECT Ch as ch, Code as code, TempAvg as temp_avg, TempMin as temp_min, TempMax as temp_max, TempMinP as temp_min_p, TempMaxP as temp_max_p FROM opt_fq_list")
        .fetch_all(&mysql_pool)
        .await
        .map_err(|e| format!("MySQL Fetch Failed: {}", e))?;
        
    let mut results = Vec::new();
    for map in mappings {
        let live = live_data.iter().find(|l| l.ch == map.dts_ch && l.code == map.dts_code);
        if let Some(l) = live {
            let temp_avg = l.temp_avg.unwrap_or(0) as f32 / 10.0;
            let temp_min = l.temp_min.unwrap_or(0) as f32 / 10.0;
            let temp_max = l.temp_max.unwrap_or(0) as f32 / 10.0;
            let temp_min_p = l.temp_min_p.unwrap_or(0);
            let temp_max_p = l.temp_max_p.unwrap_or(0);
            
            results.push(LiveSegment { id: map.id.unwrap_or(0), dts_ch: map.dts_ch, dts_code: map.dts_code, original_name: map.original_name, custom_name: map.custom_name, main_group: map.main_group, sub_group: map.sub_group, start_m: map.start_m, end_m: map.end_m, temp_avg, temp_min, temp_max, temp_min_p, temp_max_p });
        }
    }
    Ok(results)
}

#[derive(serde::Serialize)]
pub struct CurvePoint {
    pub distance: i32,
    pub temp: f32,
}

#[tauri::command]
async fn get_segment_curve(
    dts_ch: i32,
    start_m: i32,
    end_m: i32,
    state: tauri::State<'_, SqlitePool>
) -> Result<Vec<CurvePoint>, String> {
    let settings: Vec<(String, String)> = sqlx::query_as("SELECT key, value FROM settings WHERE key LIKE 'db_%'")
        .fetch_all(&*state).await.map_err(|e| e.to_string())?;
        
    let mut db_host = String::from("192.168.1.64");
    let mut db_port = String::from("58329");
    let mut db_user = String::from("root");
    let mut db_pass = String::from("l0mY4cH9H?h9");
    let mut db_name = String::from("dtscontroler");
    for (k, v) in settings { match k.as_str() { "db_host" => db_host = v, "db_port" => db_port = v, "db_user" => db_user = v, "db_pass" => db_pass = v, "db_name" => db_name = v, _ => {} } }
    
    let options = sqlx::mysql::MySqlConnectOptions::new().host(&db_host).port(db_port.parse().unwrap_or(3306)).username(&db_user).password(&db_pass).database(&db_name);
    let mysql_pool = sqlx::mysql::MySqlPoolOptions::new().max_connections(1).connect_with(options).await.map_err(|e| e.to_string())?;
    
    #[derive(sqlx::FromRow)]
    struct CurveRow { str: Option<String> }
    
    let row: Option<CurveRow> = sqlx::query_as("SELECT str FROM curvebuff WHERE Ch = ?")
        .bind(dts_ch)
        .fetch_optional(&mysql_pool)
        .await.map_err(|e| e.to_string())?;
        
    let mut points = Vec::new();
    if let Some(r) = row {
        if let Some(s) = r.str {
            let vals: Vec<&str> = s.split(',').collect();
            let end = std::cmp::min(end_m as usize, vals.len().saturating_sub(1));
            let start = std::cmp::min(start_m as usize, end);
            
            for i in start..=end {
                let t = vals[i].parse::<f32>().unwrap_or(0.0) / 10.0;
                points.push(CurvePoint { distance: i as i32, temp: t });
            }
        }
    }
    Ok(points)
}

#[derive(serde::Serialize)]
pub struct HistoryPoint {
    pub time: String,
    pub temp: f32,
}

#[tauri::command]
async fn get_segment_history(
    dts_ch: i32,
    dts_code: i32,
    limit: i32,
    state: tauri::State<'_, SqlitePool>
) -> Result<Vec<HistoryPoint>, String> {
    let settings: Vec<(String, String)> = sqlx::query_as("SELECT key, value FROM settings WHERE key LIKE 'db_%'")
        .fetch_all(&*state).await.map_err(|e| e.to_string())?;
        
    let mut db_host = String::from("192.168.1.64");
    let mut db_port = String::from("58329");
    let mut db_user = String::from("root");
    let mut db_pass = String::from("l0mY4cH9H?h9");
    let mut db_name = String::from("dtscontroler");
    for (k, v) in settings { match k.as_str() { "db_host" => db_host = v, "db_port" => db_port = v, "db_user" => db_user = v, "db_pass" => db_pass = v, "db_name" => db_name = v, _ => {} } }
    
    let options = sqlx::mysql::MySqlConnectOptions::new().host(&db_host).port(db_port.parse().unwrap_or(3306)).username(&db_user).password(&db_pass).database(&db_name);
    let mysql_pool = sqlx::mysql::MySqlPoolOptions::new().max_connections(1).connect_with(options).await.map_err(|e| e.to_string())?;
    
    #[derive(sqlx::FromRow)]
    struct HistRow { CreationTime: Option<chrono::NaiveDateTime>, TempAvg: i32 }
    
    let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
        .bind(dts_ch).bind(dts_code).bind(limit)
        .fetch_all(&mysql_pool)
        .await.map_err(|e| e.to_string())?;
        
    let mut points = Vec::new();
    for r in rows.into_iter().rev() { // reverse so oldest is first in chart
        if let Some(ct) = r.CreationTime {
            points.push(HistoryPoint { 
                time: ct.format("%H:%M:%S").to_string(), 
                temp: r.TempAvg as f32 / 10.0 
            });
        }
    }
    Ok(points)
}

#[derive(serde::Serialize)]
pub struct AlarmLog {
    pub id: i32,
    pub time: String,
    pub ch: i32,
    pub code: i32,
    pub distance: i32,
    pub alarm_type: i32,
    pub temp: f32,
    pub is_active: bool,
}

#[tauri::command]
async fn get_alarms(state: tauri::State<'_, SqlitePool>) -> Result<Vec<AlarmLog>, String> {
    let settings: Vec<(String, String)> = sqlx::query_as("SELECT key, value FROM settings WHERE key LIKE 'db_%'")
        .fetch_all(&*state).await.map_err(|e| e.to_string())?;
        
    let mut db_host = String::from("192.168.1.64");
    let mut db_port = String::from("58329");
    let mut db_user = String::from("root");
    let mut db_pass = String::from("l0mY4cH9H?h9");
    let mut db_name = String::from("dtscontroler");
    for (k, v) in settings { match k.as_str() { "db_host" => db_host = v, "db_port" => db_port = v, "db_user" => db_user = v, "db_pass" => db_pass = v, "db_name" => db_name = v, _ => {} } }
    
    let options = sqlx::mysql::MySqlConnectOptions::new().host(&db_host).port(db_port.parse().unwrap_or(3306)).username(&db_user).password(&db_pass).database(&db_name);
    let mysql_pool = sqlx::mysql::MySqlPoolOptions::new().max_connections(1).connect_with(options).await.map_err(|e| e.to_string())?;
    
    #[derive(sqlx::FromRow)]
    #[allow(non_snake_case)]
    struct AlarmRow { ID: i32, CreationTime: Option<chrono::NaiveDateTime>, Ch: Option<i32>, Code: Option<i32>, AlarmPoint: Option<i32>, AlarmCode: Option<i32>, AlarmTemp: Option<i32>, AlarmResetTime: Option<chrono::NaiveDateTime> }
    
    let rows: Vec<AlarmRow> = sqlx::query_as("SELECT ID, CreationTime, Ch, Code, AlarmPoint, AlarmCode, AlarmTemp, AlarmResetTime FROM alarmlog ORDER BY CreationTime DESC LIMIT 50")
        .fetch_all(&mysql_pool)
        .await.map_err(|e| e.to_string())?;
        
    let mut alarms = Vec::new();
    for r in rows {
        let t = r.CreationTime.map(|ct| ct.format("%H:%M:%S").to_string()).unwrap_or_default();
        let is_active = r.AlarmResetTime.is_none();
        alarms.push(AlarmLog {
            id: r.ID, time: t, ch: r.Ch.unwrap_or(0), code: r.Code.unwrap_or(0),
            distance: r.AlarmPoint.unwrap_or(0), alarm_type: r.AlarmCode.unwrap_or(0),
            temp: r.AlarmTemp.unwrap_or(0) as f32 / 10.0, is_active
        });
    }
    Ok(alarms)
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
            get_live_segments,
            get_segment_curve,
            get_segment_history,
            get_alarms,
            update_segment_mapping,
            test_db_connection
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
