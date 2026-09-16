import re

with open('src-tauri/src/db.rs', 'r') as f:
    code = f.read()

migration_code = """
    // FORCE MIGRATION: Update old map_calibration group names to the new standard
    sqlx::query("UPDATE map_calibration SET main_group = 'BEK56' WHERE main_group = 'FIBER A (TN BEK 5-6)'").execute(&pool).await?;
    sqlx::query("UPDATE map_calibration SET main_group = 'BEK34' WHERE main_group = 'FIBER B (TN BEK 3-4)'").execute(&pool).await?;
    sqlx::query("UPDATE map_calibration SET main_group = 'TCM16' WHERE main_group = 'FIBER D (TN TCM 1-6)'").execute(&pool).await?;
    sqlx::query("UPDATE map_calibration SET main_group = 'BC45-MOTOR' WHERE main_group = 'BC4B-BC5 TRANSITION'").execute(&pool).await?;
    
    // Also insert any missing ones if they somehow don't exist
    sqlx::query(
        "INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y, start_lat, start_lng, end_lat, end_lng) 
         VALUES ('TCM16', 0, 3000, 513.0, 500.0, 513.0, 800.0, -6.2, 106.8, -6.201, 106.801);"
    ).execute(&pool).await?;
    
    sqlx::query(
        "INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y, start_lat, start_lng, end_lat, end_lng) 
         VALUES ('BEK56', 0, 3000, 513.0, 200.0, 513.0, 50.0, -6.2, 106.8, -6.201, 106.801);"
    ).execute(&pool).await?;
    
    sqlx::query(
        "INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y, start_lat, start_lng, end_lat, end_lng) 
         VALUES ('BEK34', 0, 3000, 513.0, 250.0, 513.0, 150.0, -6.2, 106.8, -6.201, 106.801);"
    ).execute(&pool).await?;

    Ok(pool)
"""

code = code.replace("Ok(pool)", migration_code)

with open('src-tauri/src/db.rs', 'w') as f:
    f.write(code)

