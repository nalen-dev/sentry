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
         VALUES ('BC4B-BC5 TRANSITION', 0, 40, 1209.0, 290.0, 1241.0, 290.0, -6.2, 106.804, -6.2, 106.805);"
    ).execute(&pool).await?;

    Ok(pool)


}
