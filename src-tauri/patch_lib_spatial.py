import re

with open('src/lib.rs', 'r') as f:
    content = f.read()

spatial_func = """
#[tauri::command]
async fn get_spatial_profile(
    main_group: String,
    state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<CurvePoint>, String> {
    #[derive(sqlx::FromRow)]
    struct MapBounds {
        dts_ch: i32,
        min_start: Option<i32>,
        max_end: Option<i32>
    }
    
    let bound: Option<MapBounds> = if main_group == "All" {
        sqlx::query_as("SELECT dts_ch, MIN(start_m) as min_start, MAX(end_m) as max_end FROM segment_mappings GROUP BY dts_ch LIMIT 1")
            .fetch_optional(&*state)
            .await.map_err(|e| e.to_string())?
    } else {
        sqlx::query_as("SELECT dts_ch, MIN(start_m) as min_start, MAX(end_m) as max_end FROM segment_mappings WHERE main_group = ? GROUP BY dts_ch LIMIT 1")
            .bind(&main_group)
            .fetch_optional(&*state)
            .await.map_err(|e| e.to_string())?
    };
        
    let b = match bound {
        Some(b) => b,
        None => return Ok(Vec::new()),
    };
    
    let mysql_pool = get_mysql_pool(&state, &mysql_state).await?;
    #[derive(sqlx::FromRow)]
    struct CurveRow { str: Option<String> }
    
    let row: Option<CurveRow> = sqlx::query_as("SELECT str FROM curvebuff WHERE Ch = ?")
        .bind(b.dts_ch)
        .fetch_optional(&mysql_pool)
        .await.map_err(|e| e.to_string())?;
        
    let mut points = Vec::new();
    if let Some(r) = row {
        if let Some(s) = r.str {
            let vals: Vec<&str> = s.split(',').collect();
            let start = b.min_start.unwrap_or(0) as usize;
            let end = std::cmp::min(b.max_end.unwrap_or(vals.len() as i32) as usize, vals.len().saturating_sub(1));
            let start = std::cmp::min(start, end);
            
            for i in start..=end {
                let t = vals[i].parse::<f32>().unwrap_or(0.0) / 10.0;
                points.push(CurvePoint { distance: i as i32, temp: t });
            }
        }
    }
    Ok(points)
}
"""

if "async fn get_spatial_profile" not in content:
    content = content.replace("#[tauri::command]\nasync fn get_segment_curve", spatial_func + "\n#[tauri::command]\nasync fn get_segment_curve")

    # Add to invoke_handler
    content = content.replace("get_segment_curve,\n            get_segment_history", "get_segment_curve,\n            get_spatial_profile,\n            get_segment_history")

with open('src/lib.rs', 'w') as f:
    f.write(content)

