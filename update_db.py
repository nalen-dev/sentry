import re

with open('src-tauri/src/db.rs', 'r') as f:
    code = f.read()

# Add map_calibration table creation and default inserts
new_table_sql = """
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

    Ok(pool)
"""

code = code.replace("Ok(pool)", new_table_sql)

with open('src-tauri/src/db.rs', 'w') as f:
    f.write(code)

