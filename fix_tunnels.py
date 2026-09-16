import re

with open('src-tauri/src/db.rs', 'r') as f:
    code = f.read()

# Replace the previous TCM16/BEK56/BEK34 inserts with proper ones, and add all the subgroups!

old_inserts = """    // Also insert any missing ones if they somehow don't exist
    let _ = sqlx::query(
        "INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y, start_lat, start_lng, end_lat, end_lng) 
         VALUES ('TCM16', 0, 3000, 513.0, 500.0, 513.0, 800.0, -6.2, 106.8, -6.201, 106.801);"
    ).execute(&pool).await;
    
    let _ = sqlx::query(
        "INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y, start_lat, start_lng, end_lat, end_lng) 
         VALUES ('BEK56', 0, 3000, 513.0, 200.0, 513.0, 50.0, -6.2, 106.8, -6.201, 106.801);"
    ).execute(&pool).await;
    
    let _ = sqlx::query(
        "INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y, start_lat, start_lng, end_lat, end_lng) 
         VALUES ('BEK34', 0, 3000, 513.0, 250.0, 513.0, 150.0, -6.2, 106.8, -6.201, 106.801);"
    ).execute(&pool).await;"""

new_inserts = """    // Also insert any missing ones if they somehow don't exist
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TCM16', 0, 3000, 513.0, 314.0, 60.0, 314.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('BEK56', 0, 3000, 513.0, 274.0, 375.0, 274.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('BEK34', 0, 3000, 513.0, 282.0, 235.0, 282.0);").execute(&pool).await;

    // Fixed Subgroups for TCM16 Tunnels
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN1-2', 0, 100, 60.0, 372.0, 60.0, 314.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN2-3', 0, 100, 130.0, 372.0, 130.0, 314.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN3-4', 0, 100, 200.0, 372.0, 200.0, 314.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN4-5', 0, 100, 270.0, 372.0, 270.0, 314.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN5-6', 0, 100, 340.0, 372.0, 340.0, 314.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN6-7', 0, 100, 410.0, 372.0, 410.0, 314.0);").execute(&pool).await;

    // Fixed Subgroups for BEK
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('BEK3', 0, 100, 235.0, 220.0, 235.0, 282.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('BEK4', 0, 100, 305.0, 220.0, 305.0, 282.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('BEK5', 0, 100, 375.0, 220.0, 375.0, 274.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('BEK6', 0, 100, 445.0, 220.0, 445.0, 274.0);").execute(&pool).await;"""

code = code.replace(old_inserts, new_inserts)

with open('src-tauri/src/db.rs', 'w') as f:
    f.write(code)

