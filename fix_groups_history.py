import re

with open('src-tauri/src/lib.rs', 'r') as f:
    lib = f.read()

old_gh = """async fn get_groups_history(
    limit: i32,
    state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<GroupHistoryPoint>, String> {
    // 1. Get mappings from SQLite
    let mappings: Vec<crate::domain::app_models::SegmentMapping> = sqlx::query_as("SELECT * FROM segment_mappings WHERE main_group != 'Unassigned'")
        .fetch_all(&*state).await.map_err(|e| e.to_string())?;
        
    let mysql_pool = get_mysql_pool(&state, &mysql_state).await?;
    
    #[derive(sqlx::FromRow)]
    #[allow(non_snake_case)]
    struct HistRow { CreationTime: Option<chrono::DateTime<chrono::Utc>>, TempAvg: Option<i32> }
    
    // GroupName -> (Time -> Vec<Temp>)
    let mut group_data: std::collections::HashMap<String, std::collections::HashMap<String, Vec<f32>>> = std::collections::HashMap::new();
    
    for map in mappings {
        let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
            .bind(map.dts_ch).bind(map.dts_code).bind(limit)
            .fetch_all(&mysql_pool)
            .await.unwrap_or_default();
            
        for r in rows {"""

new_gh = """async fn get_groups_history(
    minutes: i32,
    state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<GroupHistoryPoint>, String> {
    // 1. Get mappings from SQLite
    let mappings: Vec<crate::domain::app_models::SegmentMapping> = sqlx::query_as("SELECT * FROM segment_mappings WHERE main_group != 'Unassigned'")
        .fetch_all(&*state).await.map_err(|e| e.to_string())?;
        
    let mysql_pool = get_mysql_pool(&state, &mysql_state).await?;
    
    #[derive(sqlx::FromRow)]
    #[allow(non_snake_case)]
    struct HistRow { CreationTime: Option<chrono::DateTime<chrono::Utc>>, TempAvg: Option<i32> }
    
    // GroupName -> (Time -> Vec<Temp>)
    let mut group_data: std::collections::HashMap<String, std::collections::HashMap<String, Vec<f32>>> = std::collections::HashMap::new();
    
    let limit = minutes * 10;
    
    for map in mappings {
        let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
            .bind(map.dts_ch).bind(map.dts_code).bind(limit)
            .fetch_all(&mysql_pool)
            .await.unwrap_or_default();
            
        if rows.is_empty() { continue; }
        let latest_time = rows[0].CreationTime.unwrap_or_default();
        let cutoff_time = latest_time - chrono::Duration::minutes(minutes as i64);
            
        for r in rows {
            if let Some(ct) = r.CreationTime {
                if ct < cutoff_time { continue; }
"""

lib = lib.replace(old_gh, new_gh)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(lib)

