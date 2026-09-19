use sqlx::{sqlite::SqlitePoolOptions, SqlitePool};
use std::fs;
use std::path::PathBuf;

pub async fn init_db(app_dir: &PathBuf) -> Result<SqlitePool, sqlx::Error> {
    // Ensure the application directory exists
    if !app_dir.exists() {
        fs::create_dir_all(app_dir).expect("Failed to create app data directory");
    }

    let db_path = app_dir.join("sentry_scada.db");
    let db_url = format!("sqlite://{}?mode=rwc", db_path.display());

    let pool = SqlitePoolOptions::new()
        .max_connections(5)
        .connect(&db_url)
        .await?;

    // Create tables if they don't exist
    sqlx::query(
        "CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            status TEXT NOT NULL
        );"
    )
    .execute(&pool)
    .await?;

    // Insert default admin if not exists
    sqlx::query(
        "INSERT OR IGNORE INTO users (id, role, status) VALUES ('ADMIN-01', 'ADMINISTRATOR', 'Active');"
    )
    .execute(&pool)
    .await?;

    sqlx::query(
        "CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );"
    )
    .execute(&pool)
    .await?;

    // Insert default thresholds
    sqlx::query(
        "INSERT OR IGNORE INTO settings (key, value) VALUES ('warning_threshold', '60.0');"
    )
    .execute(&pool)
    .await?;

    sqlx::query(
        "INSERT OR IGNORE INTO settings (key, value) VALUES ('critical_threshold', '70.0');"
    )
    .execute(&pool)
    .await?;

    sqlx::query(
        "CREATE TABLE IF NOT EXISTS alarm_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            segment TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT NOT NULL
        );"
    )
    .execute(&pool)
    .await?;

    sqlx::query(
        "CREATE TABLE IF NOT EXISTS segment_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dts_ch INTEGER NOT NULL,
            dts_code INTEGER NOT NULL,
            original_name TEXT NOT NULL,
            custom_name TEXT,
            main_group TEXT NOT NULL,
            sub_group TEXT,
            start_m INTEGER,
            end_m INTEGER,
            UNIQUE(dts_ch, dts_code)
        );"
    )
    .execute(&pool)
    .await?;

    // Try to add start_m and end_m if they don't exist
    let _ = sqlx::query("ALTER TABLE segment_mappings ADD COLUMN start_m INTEGER").execute(&pool).await;
    let _ = sqlx::query("ALTER TABLE segment_mappings ADD COLUMN end_m INTEGER").execute(&pool).await;

    
    sqlx::query(
        "CREATE TABLE IF NOT EXISTS map_calibration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_group TEXT NOT NULL UNIQUE,
            start_m INTEGER NOT NULL,
            end_m INTEGER NOT NULL,
            start_svg_x REAL NOT NULL,
            start_svg_y REAL NOT NULL,
            end_svg_x REAL NOT NULL,
            end_svg_y REAL NOT NULL,
            start_lat REAL,
            start_lng REAL,
            end_lat REAL,
            end_lng REAL
        );"
    )
    .execute(&pool)
    .await?;

    // Insert Default Calibration for BC4 A
    sqlx::query(
        "INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y, start_lat, start_lng, end_lat, end_lng) 
         VALUES ('BC4 A', 0, 591, 513.0, 290.0, 40.0, 290.0, -6.2, 106.8, -6.201, 106.801);"
    ).execute(&pool).await?;

    // Insert Default Calibration for BC4 B
    sqlx::query(
        "INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y, start_lat, start_lng, end_lat, end_lng) 
         VALUES ('BC4 B', 0, 877, 513.0, 314.0, 1225.0, 314.0, -6.2, 106.8, -6.2, 106.805);"
    ).execute(&pool).await?;

    // Insert Default Calibration for BC5
    sqlx::query(
        "INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y, start_lat, start_lng, end_lat, end_lng) 
         VALUES ('BC5', 0, 150, 1235.0, 314.0, 1355.0, 314.0, -6.2, 106.805, -6.2, 106.807);"
    ).execute(&pool).await?;

    
    // Insert Default Calibration for BC4B-BC5 Transition
    sqlx::query(
        "INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y, start_lat, start_lng, end_lat, end_lng) 
         VALUES ('BC45-MOTOR', 0, 40, 1209.0, 290.0, 1241.0, 290.0, -6.2, 106.804, -6.2, 106.805);"
    ).execute(&pool).await?;

    
    // FORCE MIGRATION: Update old map_calibration group names
    let _ = sqlx::query("UPDATE OR IGNORE map_calibration SET main_group = 'BEK56' WHERE main_group = 'FIBER A (TN BEK 5-6)'").execute(&pool).await;
    let _ = sqlx::query("UPDATE OR IGNORE map_calibration SET main_group = 'BEK34' WHERE main_group = 'FIBER B (TN BEK 3-4)'").execute(&pool).await;
    let _ = sqlx::query("UPDATE OR IGNORE map_calibration SET main_group = 'TCM16' WHERE main_group = 'FIBER D (TN TCM 1-6)'").execute(&pool).await;
    let _ = sqlx::query("UPDATE OR IGNORE map_calibration SET main_group = 'BC45-MOTOR' WHERE main_group = 'BC4B-BC5 TRANSITION'").execute(&pool).await;
    
    // Clean up old experiment subgroups from previous run
    let _ = sqlx::query("DELETE FROM map_calibration WHERE main_group IN ('TN1-2', 'TN2-3', 'TN3-4', 'TN4-5', 'TN5-6', 'TN6-7', 'BEK3', 'BEK4', 'BEK5', 'BEK6')").execute(&pool).await;

    // INSERT EXACT SUBGROUPS AS DEFINED BY USER (stored as main_group in map_calibration for coordinate matching)
    
    // line TCM16
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN12', 0, 100, 60.0, 314.0, 130.0, 314.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN23', 0, 100, 130.0, 314.0, 200.0, 314.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN34', 0, 100, 200.0, 314.0, 270.0, 314.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN45', 0, 100, 270.0, 314.0, 340.0, 314.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN56', 0, 100, 340.0, 314.0, 410.0, 314.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN6CR', 0, 100, 410.0, 314.0, 513.0, 314.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TCM6CR', 0, 100, 410.0, 314.0, 513.0, 314.0);").execute(&pool).await;

    // line BEK34
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('BE34M', 0, 100, 235.0, 282.0, 305.0, 282.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('BEK4CR', 0, 100, 305.0, 282.0, 513.0, 282.0);").execute(&pool).await;

    // line BEK56
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('BEK56M', 0, 100, 375.0, 274.0, 445.0, 274.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('BEK6CR', 0, 100, 445.0, 274.0, 513.0, 274.0);").execute(&pool).await;


    Ok(pool)



}
