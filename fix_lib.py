import re

with open('src-tauri/src/lib.rs', 'r') as f:
    code = f.read()

# Fix 1: Stop update_segment_mapping from wiping start_m and end_m
old_update = """async fn update_segment_mapping(
    id: i32, 
    custom_name: Option<String>, 
    main_group: String,
    sub_group: Option<String>,
    start_m: Option<f64>,
    end_m: Option<f64>,
    state: tauri::State<'_, SqlitePool>
) -> Result<(), String> {
    let _ = sqlx::query("UPDATE segment_mappings SET custom_name = ?, main_group = ?, sub_group = ?, start_m = ?, end_m = ? WHERE id = ?")
        .bind(custom_name)
        .bind(main_group)
        .bind(sub_group)
        .bind(start_m)
        .bind(end_m)
        .bind(id)"""

new_update = """async fn update_segment_mapping(
    id: i32, 
    custom_name: Option<String>, 
    main_group: String,
    sub_group: Option<String>,
    start_m: Option<f64>,
    end_m: Option<f64>,
    state: tauri::State<'_, SqlitePool>
) -> Result<(), String> {
    // Only update mapping fields, NEVER overwrite start_m or end_m with null from the UI!
    let _ = sqlx::query("UPDATE segment_mappings SET custom_name = ?, main_group = ?, sub_group = ? WHERE id = ?")
        .bind(custom_name)
        .bind(main_group)
        .bind(sub_group)
        .bind(id)"""

code = code.replace(old_update, new_update)

# Fix 2: Stop sync_dts_segments from wiping the whole table
old_sync = """    // Wipe old data completely (replace)
    let _ = sqlx::query("DELETE FROM segment_mappings").execute(&*state).await;

    // 4. Sync to SQLite
    let mut new_added = 0;
    for row in &rows {
        if let Some(code) = row.code {
            let original_name = row.fq_table.clone().unwrap_or_else(|| format!("CSection{}", code));
            
            let result = sqlx::query(
                "INSERT INTO segment_mappings (dts_ch, dts_code, original_name, main_group, start_m, end_m) 
                 VALUES (?, ?, ?, 'Unassigned', ?, ?)"
            )"""

new_sync = """    // We no longer wipe the table! We upsert to preserve the user's mapping assignments.

    // 4. Sync to SQLite
    let mut new_added = 0;
    for row in &rows {
        if let Some(code) = row.code {
            let original_name = row.fq_table.clone().unwrap_or_else(|| format!("CSection{}", code));
            
            let result = sqlx::query(
                "INSERT INTO segment_mappings (dts_ch, dts_code, original_name, main_group, start_m, end_m) 
                 VALUES (?, ?, ?, 'Unassigned', ?, ?) 
                 ON CONFLICT(dts_ch, dts_code) 
                 DO UPDATE SET start_m = excluded.start_m, end_m = excluded.end_m, original_name = excluded.original_name"
            )"""

code = code.replace(old_sync, new_sync)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(code)

