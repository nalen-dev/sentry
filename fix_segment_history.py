import re

with open('src-tauri/src/lib.rs', 'r') as f:
    lib = f.read()

# I will use a regex to replace the function entirely
pattern = re.compile(
    r"async fn get_segment_history.*?Ok\(points\)\n\}",
    re.DOTALL
)

new_sh = """async fn get_segment_history(
    dts_ch: i32,
    dts_code: i32,
    minutes: i32,
    state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<HistoryPoint>, String> {
    let mysql_pool = get_mysql_pool(&state, &mysql_state).await?;
    #[derive(sqlx::FromRow)]
    #[allow(non_snake_case)]
    struct HistRow { CreationTime: Option<chrono::DateTime<chrono::Utc>>, TempAvg: Option<i32> }
    
    let limit = minutes * 10;
    
    let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
        .bind(dts_ch).bind(dts_code).bind(limit)
        .fetch_all(&mysql_pool)
        .await.map_err(|e| e.to_string())?;
        
    let mut points = Vec::new();
    if rows.is_empty() { return Ok(points); }
    let latest_time = rows[0].CreationTime.unwrap_or_default();
    let cutoff_time = latest_time - chrono::Duration::minutes(minutes as i64);
    
    for r in rows.into_iter().rev() {
        if let Some(ct) = r.CreationTime {
            if ct < cutoff_time { continue; }
            let temp = r.TempAvg.unwrap_or(0) as f32 / 10.0;
            if temp >= 0.0 {
                points.push(HistoryPoint { 
                    time: ct.with_timezone(&chrono::Local).format("%H:%M").to_string(), 
                    temp 
                });
            }
        }
    }
    Ok(points)
}"""

lib = pattern.sub(new_sh, lib, count=1)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(lib)

