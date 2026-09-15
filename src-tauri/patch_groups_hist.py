import re

with open('src/lib.rs', 'r') as f:
    content = f.read()

new_command = """
#[derive(serde::Serialize)]
pub struct GroupHistoryPoint {
    pub time: String,
    pub groups: std::collections::HashMap<String, f32>,
}

#[tauri::command]
async fn get_groups_history(
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
            
        for r in rows {
            if let Some(ct) = r.CreationTime {
                // Round time to nearest minute to group them easily, or just use HH:MM
                let t_str = ct.format("%H:%M").to_string();
                let temp = r.TempAvg.unwrap_or(0) as f32 / 10.0;
                
                group_data
                    .entry(map.main_group.clone())
                    .or_default()
                    .entry(t_str)
                    .or_default()
                    .push(temp);
            }
        }
    }
    
    // Now aggregate into Vec<GroupHistoryPoint>
    // First, collect all unique times
    let mut all_times = std::collections::HashSet::new();
    for times in group_data.values() {
        for t in times.keys() {
            all_times.insert(t.clone());
        }
    }
    
    let mut sorted_times: Vec<String> = all_times.into_iter().collect();
    sorted_times.sort();
    
    // Keep only the last `limit` times globally
    if sorted_times.len() > limit as usize {
        let skip = sorted_times.len() - limit as usize;
        sorted_times = sorted_times.into_iter().skip(skip).collect();
    }
    
    let mut results = Vec::new();
    for t in sorted_times {
        let mut groups_map = std::collections::HashMap::new();
        for (g_name, times_map) in &group_data {
            if let Some(temps) = times_map.get(&t) {
                let sum: f32 = temps.iter().sum();
                let avg = sum / temps.len() as f32;
                groups_map.insert(g_name.clone(), avg);
            }
        }
        results.push(GroupHistoryPoint { time: t, groups: groups_map });
    }
    
    Ok(results)
}
"""

# Insert before get_alarms
content = content.replace("#[derive(serde::Serialize)]\npub struct AlarmLog {", new_command + "\n#[derive(serde::Serialize)]\npub struct AlarmLog {")

# Register in run()
content = content.replace("get_segment_history,", "get_segment_history, get_groups_history,")

with open('src/lib.rs', 'w') as f:
    f.write(content)
