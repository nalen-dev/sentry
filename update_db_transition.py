import re

with open('src-tauri/src/db.rs', 'r') as f:
    code = f.read()

transition_default = """
    // Insert Default Calibration for BC4B-BC5 Transition
    sqlx::query(
        "INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y, start_lat, start_lng, end_lat, end_lng) 
         VALUES ('BC4B-BC5 TRANSITION', 0, 40, 1209.0, 290.0, 1241.0, 290.0, -6.2, 106.804, -6.2, 106.805);"
    ).execute(&pool).await?;

    Ok(pool)
"""

code = code.replace("Ok(pool)", transition_default)

with open('src-tauri/src/db.rs', 'w') as f:
    f.write(code)

