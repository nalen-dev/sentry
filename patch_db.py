import re

with open('src-tauri/src/db.rs', 'r') as f:
    code = f.read()

target = """    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN34', 0, 100, 200.0, 314.0, 270.0, 314.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN56', 0, 100, 340.0, 314.0, 410.0, 314.0);").execute(&pool).await;"""

replacement = """    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN34', 0, 100, 200.0, 314.0, 270.0, 314.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN45', 0, 100, 270.0, 314.0, 340.0, 314.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN56', 0, 100, 340.0, 314.0, 410.0, 314.0);").execute(&pool).await;"""

code = code.replace(target, replacement)

code = code.replace(
    """let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN6CR', 0, 100, 410.0, 314.0, 513.0, 314.0);").execute(&pool).await;""",
    """let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN6CR', 0, 100, 410.0, 314.0, 513.0, 314.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TCM6CR', 0, 100, 410.0, 314.0, 513.0, 314.0);").execute(&pool).await;"""
)

with open('src-tauri/src/db.rs', 'w') as f:
    f.write(code)

