import re

with open('src/lib.rs', 'r') as f:
    content = f.read()

# Extract the old get_history_summary
start_idx = content.find("async fn get_history_summary")
end_idx = content.find("#[tauri::command]", start_idx + 10)

if start_idx != -1 and end_idx != -1:
    old_func = content[start_idx:end_idx]
    
    new_func = """async fn get_history_summary(
    start_dt: String,
    end_dt: String,
    state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Option<HistorySummary>, String> {
    use chrono::{Local, TimeZone, NaiveDateTime};
    let parsed_start = Local.from_local_datetime(&NaiveDateTime::parse_from_str(&start_dt, "%Y-%m-%d %H:%M:%S").map_err(|e| e.to_string())?).unwrap();
    let parsed_end = Local.from_local_datetime(&NaiveDateTime::parse_from_str(&end_dt, "%Y-%m-%d %H:%M:%S").map_err(|e| e.to_string())?).unwrap();

    let mysql_pool = get_mysql_pool(&state, &mysql_state).await?;
    let mappings = get_segment_mappings(state.clone()).await.unwrap_or_default();
    
    #[derive(sqlx::FromRow, Clone)]
    #[allow(non_snake_case)]
    struct HistRow { CreationTime: Option<chrono::DateTime<chrono::Local>>, TempAvg: Option<i32> }

    let mut overall_max_temp: i32 = -999999;
    let mut overall_max_time: String = String::new();
    let mut overall_max_group: String = String::new();
    let mut overall_max_segment: String = String::new();

    let mut overall_min_temp: i32 = 999999;
    let mut overall_min_time: String = String::new();
    let mut overall_min_group: String = String::new();
    let mut overall_min_segment: String = String::new();

    let mut found_any = false;

    for map in mappings {
        if map.main_group == "Unassigned" {
            continue;
        }

        let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? AND CreationTime >= ? AND CreationTime <= ? ORDER BY CreationTime ASC LIMIT 2000")
            .bind(map.dts_ch).bind(map.dts_code).bind(parsed_start).bind(parsed_end)
            .fetch_all(&mysql_pool)
            .await.unwrap_or_default();

        let name = if let Some(c) = &map.custom_name { if c.is_empty() { map.original_name.clone() } else { c.clone() } } else { map.original_name.clone() };

        for r in rows {
            if let Some(t) = r.TempAvg {
                if t >= 0 {
                    found_any = true;
                    if t > overall_max_temp {
                        overall_max_temp = t;
                        overall_max_time = r.CreationTime.map(|c| c.format("%H:%M:%S").to_string()).unwrap_or_default();
                        overall_max_group = map.main_group.clone();
                        overall_max_segment = name.clone();
                    }
                    if t < overall_min_temp {
                        overall_min_temp = t;
                        overall_min_time = r.CreationTime.map(|c| c.format("%H:%M:%S").to_string()).unwrap_or_default();
                        overall_min_group = map.main_group.clone();
                        overall_min_segment = name.clone();
                    }
                }
            }
        }
    }

    if !found_any {
        return Ok(None);
    }

    Ok(Some(HistorySummary {
        max_temp: overall_max_temp as f32 / 10.0,
        max_time: overall_max_time,
        max_group: overall_max_group,
        max_segment: overall_max_segment,
        min_temp: overall_min_temp as f32 / 10.0,
        min_time: overall_min_time,
        min_group: overall_min_group,
        min_segment: overall_min_segment,
    }))
}

"""
    content = content.replace(old_func, new_func)

    with open('src/lib.rs', 'w') as f:
        f.write(content)
else:
    print("Could not find function bounds")
