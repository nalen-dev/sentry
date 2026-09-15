import re

with open('src-tauri/src/lib.rs', 'r') as f:
    lib = f.read()

# Replace the get_groups_history logic
pattern = re.compile(
    r"async fn get_groups_history.*?let mut all_times = std::collections::HashSet::new\(\);",
    re.DOTALL
)

new_gh = """async fn get_groups_history(
    minutes: i32,
    state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<GroupHistoryPoint>, String> {
    let mappings: Vec<crate::domain::app_models::SegmentMapping> = sqlx::query_as("SELECT * FROM segment_mappings WHERE main_group != 'Unassigned'")
        .fetch_all(&*state).await.map_err(|e| e.to_string())?;
        
    let mysql_pool = get_mysql_pool(&state, &mysql_state).await?;
    
    #[derive(sqlx::FromRow, Clone)]
    #[allow(non_snake_case)]
    struct HistRow { CreationTime: Option<chrono::DateTime<chrono::Utc>>, TempAvg: Option<i32>, Ch: i32, Code: i32 }
    
    let limit = minutes * 10;
    
    struct FetchedSeg {
        group: String,
        rows: Vec<HistRow>,
    }
    
    let mut all_fetched: Vec<FetchedSeg> = Vec::new();
    let mut global_max_time: Option<chrono::DateTime<chrono::Utc>> = None;
    
    for map in mappings {
        let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
            .bind(map.dts_ch).bind(map.dts_code).bind(limit)
            .fetch_all(&mysql_pool)
            .await.unwrap_or_default();
            
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
            for r in seg.rows {
                if let Some(ct) = r.CreationTime {
                    if ct < cutoff_time { continue; }
                    
                    let t_str = ct.with_timezone(&chrono::Local).format("%H:%M").to_string();
                    let temp = r.TempAvg.unwrap_or(0) as f32 / 10.0;
                    if temp >= 0.0 {
                        group_data
                            .entry(seg.group.clone())
                            .or_default()
                            .entry(t_str)
                            .or_default()
                            .push(temp);
                    }
                }
            }
        }
    }
    
    let mut all_times = std::collections::HashSet::new();"""

lib = pattern.sub(new_gh, lib, count=1)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(lib)


# 2. Fix the ChartPage.tsx to default to 'spatial'
with open('src/pages/ChartPage.tsx', 'r') as f:
    cp = f.read()

cp = cp.replace(
    "const [chartMode, setChartMode] = useState<'history' | 'spatial'>('history');",
    "const [chartMode, setChartMode] = useState<'history' | 'spatial'>('spatial');"
)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(cp)

