with open('src/lib.rs', 'r') as f:
    content = f.read()

# I will find the start and end indices of get_groups_history
start_str = "#[tauri::command]\nasync fn get_groups_history("
start_idx = content.find(start_str)

end_str = "Ok(results)\n}"
end_idx = content.find(end_str, start_idx) + len(end_str)

old_func = content[start_idx:end_idx]

new_func = """#[tauri::command]
async fn get_groups_history(
    start_dt: String,
    end_dt: String,
    state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<GroupHistoryPoint>, String> {
    let mappings: Vec<crate::domain::app_models::SegmentMapping> = sqlx::query_as("SELECT * FROM segment_mappings WHERE main_group != 'Unassigned'")
        .fetch_all(&*state).await.map_err(|e| e.to_string())?;
        
    let mysql_pool = get_mysql_pool(&state, &mysql_state).await?;
    
    #[derive(sqlx::FromRow, Clone)]
    #[allow(non_snake_case)]
    struct HistRow { CreationTime: Option<chrono::DateTime<chrono::Utc>>, TempAvg: Option<i32>, Ch: i32, Code: i32 }
    
    struct FetchedSeg {
        group: String,
        rows: Vec<HistRow>,
    }
    
    let mut all_fetched: Vec<FetchedSeg> = Vec::new();
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
    }
    
    let mut points: Vec<GroupHistoryPoint> = group_data.into_iter().map(|(time, groups)| {
        let max_groups = groups.into_iter().map(|(g, temps)| {
            let max_temp = temps.into_iter().fold(f32::NEG_INFINITY, f32::max);
            (g, max_temp)
        }).collect();
        GroupHistoryPoint { time, groups: max_groups }
    }).collect();
    
    points.sort_by(|a, b| a.time.cmp(&b.time));
    Ok(points)
}"""

content = content[:start_idx] + new_func + content[end_idx:]

with open('src/lib.rs', 'w') as f:
    f.write(content)

