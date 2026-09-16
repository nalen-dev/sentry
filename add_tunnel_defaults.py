import re

with open('src-tauri/src/db.rs', 'r') as f:
    code = f.read()

tunnel_defaults = """
    // Insert Default Calibration for Fiber A (TN BEK 5-6)
    sqlx::query(
        "INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y, start_lat, start_lng, end_lat, end_lng) 
         VALUES ('FIBER A (TN BEK 5-6)', 0, 1000, 513.0, 274.0, 375.0, 274.0, -6.2, 106.8, -6.2, 106.8);"
    ).execute(&pool).await?;

    // Insert Default Calibration for Fiber B (TN BEK 3-4)
    sqlx::query(
        "INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y, start_lat, start_lng, end_lat, end_lng) 
         VALUES ('FIBER B (TN BEK 3-4)', 0, 1000, 513.0, 282.0, 235.0, 282.0, -6.2, 106.8, -6.2, 106.8);"
    ).execute(&pool).await?;

    // Insert Default Calibration for Fiber D (TN TCM 1-6)
    sqlx::query(
        "INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y, start_lat, start_lng, end_lat, end_lng) 
         VALUES ('FIBER D (TN TCM 1-6)', 0, 2000, 513.0, 314.0, 60.0, 314.0, -6.2, 106.8, -6.2, 106.8);"
    ).execute(&pool).await?;

    Ok(pool)
"""

code = code.replace("Ok(pool)", tunnel_defaults)

with open('src-tauri/src/db.rs', 'w') as f:
    f.write(code)

