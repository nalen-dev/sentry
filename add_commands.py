import re

with open('src-tauri/src/lib.rs', 'r') as f:
    code = f.read()

# Add get_map_calibration and save_map_calibration functions
calibration_funcs = """
#[tauri::command]
async fn get_map_calibration(state: tauri::State<'_, SqlitePool>) -> Result<Vec<crate::domain::app_models::MapCalibration>, String> {
    let rows: Vec<crate::domain::app_models::MapCalibration> = sqlx::query_as("SELECT * FROM map_calibration ORDER BY id")
        .fetch_all(&*state)
        .await
        .map_err(|e| e.to_string())?;
    Ok(rows)
}

#[tauri::command]
async fn save_map_calibration(state: tauri::State<'_, SqlitePool>, calib: crate::domain::app_models::MapCalibration) -> Result<(), String> {
    if let Some(id) = calib.id {
        sqlx::query(
            "UPDATE map_calibration SET main_group = ?, start_m = ?, end_m = ?, start_svg_x = ?, start_svg_y = ?, end_svg_x = ?, end_svg_y = ?, start_lat = ?, start_lng = ?, end_lat = ?, end_lng = ? WHERE id = ?"
        )
        .bind(&calib.main_group)
        .bind(calib.start_m)
        .bind(calib.end_m)
        .bind(calib.start_svg_x)
        .bind(calib.start_svg_y)
        .bind(calib.end_svg_x)
        .bind(calib.end_svg_y)
        .bind(calib.start_lat)
        .bind(calib.start_lng)
        .bind(calib.end_lat)
        .bind(calib.end_lng)
        .bind(id)
        .execute(&*state)
        .await
        .map_err(|e| e.to_string())?;
    } else {
        sqlx::query(
            "INSERT INTO map_calibration (main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y, start_lat, start_lng, end_lat, end_lng) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        .bind(&calib.main_group)
        .bind(calib.start_m)
        .bind(calib.end_m)
        .bind(calib.start_svg_x)
        .bind(calib.start_svg_y)
        .bind(calib.end_svg_x)
        .bind(calib.end_svg_y)
        .bind(calib.start_lat)
        .bind(calib.start_lng)
        .bind(calib.end_lat)
        .bind(calib.end_lng)
        .execute(&*state)
        .await
        .map_err(|e| e.to_string())?;
    }
    Ok(())
}
"""

# Insert before run function
code = code.replace("pub fn run() {", calibration_funcs + "\npub fn run() {")

# Register commands
invoke_handler = "            get_app_settings,\n            save_app_setting,\n            get_map_calibration,\n            save_map_calibration,"
code = code.replace("            get_app_settings,\n            save_app_setting,", invoke_handler)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(code)

