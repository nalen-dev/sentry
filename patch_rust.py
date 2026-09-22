import re

with open('src-tauri/src/lib.rs', 'r') as f:
    content = f.read()

# Replace get_groups_history
old_signature = """#[tauri::command]
async fn get_groups_history(
    minutes: i32,
    date: Option<String>,
    state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<GroupHistoryPoint>, String> {"""

new_signature = """#[tauri::command]
async fn get_groups_history(
    start_dt: String,
    end_dt: String,
    state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<GroupHistoryPoint>, String> {"""

content = content.replace(old_signature, new_signature)

# Now replace the query logic inside get_groups_history
old_query_logic = """    let mut all_fetched: Vec<FetchedSeg> = Vec::new();
    let mut global_max_time: Option<chrono::DateTime<chrono::Utc>> = None;
    
    for map in mappings {
        let rows: Vec<HistRow> = if let Some(ref d) = date {
            sqlx::query_as("SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? AND CreationTime >= ? AND CreationTime < DATE_ADD(?, INTERVAL 1 DAY) ORDER BY CreationTime DESC LIMIT ?")
                .bind(map.dts_ch).bind(map.dts_code).bind(d.clone()).bind(d).bind(limit)
                .fetch_all(&mysql_pool)
                .await.unwrap_or_default()
        } else {
            sqlx::query_as("SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
                .bind(map.dts_ch).bind(map.dts_code).bind(limit)
                .fetch_all(&mysql_pool)
                .await.unwrap_or_default()
        };
            
        if !rows.is_empty() {
            if let Some(ct) = rows[0].CreationTime {
                if global_max_time.is_none() || ct > global_max_time.unwrap() {
                    global_max_time = Some(ct);
                }
            }
        }
        all_fetched.push(FetchedSeg { group: map.main_group.clone(), rows });
    }
    
    let mut group_data: std::collections::HashMap<String, std::collections::HashMap<String, Vec<f32>>> = std::collections::HashMap::new();
    
    if let Some(max_time) = global_max_time {
        let cutoff_time = max_time - chrono::Duration::minutes(minutes as i64);
        
        for seg in all_fetched {
            let group_name = seg.group;
            for r in seg.rows {
                if let Some(ct) = r.CreationTime {
                    if ct >= cutoff_time {
                        let time_str = ct.with_timezone(&chrono::Local).format("%H:%M").to_string();
                        let temp = r.TempAvg.unwrap_or(0) as f32 / 10.0;
                        if temp >= 0.0 {
                            let entry = group_data.entry(time_str).or_default();
                            entry.entry(group_name.clone()).or_default().push(temp);
                        }
                    }
                }
            }
        }
    }"""

new_query_logic = """    let mut all_fetched: Vec<FetchedSeg> = Vec::new();
    
    // Safety limit per query to prevent crashing on large ranges
    let limit = 2000;
    
    for map in mappings {
        let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? AND CreationTime >= ? AND CreationTime <= ? ORDER BY CreationTime ASC LIMIT ?")
            .bind(map.dts_ch).bind(map.dts_code).bind(&start_dt).bind(&end_dt).bind(limit)
            .fetch_all(&mysql_pool)
            .await.unwrap_or_default();
            
        all_fetched.push(FetchedSeg { group: map.main_group.clone(), rows });
    }
    
    let mut group_data: std::collections::HashMap<String, std::collections::HashMap<String, Vec<f32>>> = std::collections::HashMap::new();
    
    for seg in all_fetched {
        let group_name = seg.group;
        for r in seg.rows {
            if let Some(ct) = r.CreationTime {
                let time_str = ct.with_timezone(&chrono::Local).format("%H:%M").to_string();
                let temp = r.TempAvg.unwrap_or(0) as f32 / 10.0;
                if temp >= 0.0 {
                    let entry = group_data.entry(time_str).or_default();
                    entry.entry(group_name.clone()).or_default().push(temp);
                }
            }
        }
    }"""

content = content.replace(old_query_logic, new_query_logic)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(content)

