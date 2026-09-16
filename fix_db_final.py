import re

with open('src-tauri/src/db.rs', 'r') as f:
    code = f.read()

# I will replace the whole migration block with a clean slate
# First, clear the map_calibration table of all the TN1-2, BEK3, BEK4 crap I added before.
# Then insert the EXACT ones the user specified.

migration_block_old_start = "// FORCE MIGRATION: Update old map_calibration group names to the new standard (ignore errors if they fail due to uniqueness constraints)"
migration_block_old_end = "let _ = sqlx::query(\"INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('BEK6', 0, 100, 445.0, 220.0, 445.0, 274.0);\").execute(&pool).await;"

# Find the exact text to replace
match = re.search(re.escape(migration_block_old_start) + r'.*?' + re.escape(migration_block_old_end), code, re.DOTALL)
if match:
    new_migration = """// FORCE MIGRATION: Update old map_calibration group names
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
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN56', 0, 100, 340.0, 314.0, 410.0, 314.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('TN6CR', 0, 100, 410.0, 314.0, 513.0, 314.0);").execute(&pool).await;

    // line BEK34
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('BE34M', 0, 100, 235.0, 282.0, 305.0, 282.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('BEK4CR', 0, 100, 305.0, 282.0, 513.0, 282.0);").execute(&pool).await;

    // line BEK56
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('BEK56M', 0, 100, 375.0, 274.0, 445.0, 274.0);").execute(&pool).await;
    let _ = sqlx::query("INSERT OR IGNORE INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y) VALUES ('BEK6CR', 0, 100, 445.0, 274.0, 513.0, 274.0);").execute(&pool).await;
"""
    code = code[:match.start()] + new_migration + code[match.end():]
    
    with open('src-tauri/src/db.rs', 'w') as f:
        f.write(code)

