import re

with open('src/lib.rs', 'r') as f:
    content = f.read()

# Locate the get_history_summary function
start_idx = content.find("let mut found_any = false;")
end_idx = content.find("let name = if let Some(c) = &map.custom_name", start_idx)

if start_idx != -1 and end_idx != -1:
    new_logic = """let mut found_any = false;

    // Pre-calculate smart names to match frontend logic
    use std::collections::HashMap;
    let mut grouped_segs: HashMap<String, Vec<&crate::domain::app_models::SegmentMapping>> = HashMap::new();
    for map in &mappings {
        if map.main_group != "Unassigned" {
            let prefix = if let Some(sg) = &map.sub_group { if sg.is_empty() { map.main_group.clone() } else { sg.clone() } } else { map.main_group.clone() };
            grouped_segs.entry(prefix).or_default().push(map);
        }
    }
    
    let mut smart_names: HashMap<(i32, i32), String> = HashMap::new();
    for (prefix, mut segs) in grouped_segs {
        segs.sort_by_key(|m| m.start_m.unwrap_or(0));
        for (i, m) in segs.iter().enumerate() {
            smart_names.insert((m.dts_ch, m.dts_code), format!("{} - {}", prefix, i + 1));
        }
    }

    for map in mappings {
        if map.main_group == "Unassigned" {
            continue;
        }

        let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? AND CreationTime >= ? AND CreationTime <= ? ORDER BY CreationTime ASC LIMIT 2000")
            .bind(map.dts_ch).bind(map.dts_code).bind(parsed_start).bind(parsed_end)
            .fetch_all(&mysql_pool)
            .await.unwrap_or_default();

        let name = smart_names.get(&(map.dts_ch, map.dts_code))
            .cloned()
            .unwrap_or_else(|| if let Some(c) = &map.custom_name { if c.is_empty() { map.original_name.clone() } else { c.clone() } } else { map.original_name.clone() });
"""
    # Replace the old logic
    old_target = """let mut found_any = false;

    for map in mappings {
        if map.main_group == "Unassigned" {
            continue;
        }

        let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? AND CreationTime >= ? AND CreationTime <= ? ORDER BY CreationTime ASC LIMIT 2000")
            .bind(map.dts_ch).bind(map.dts_code).bind(parsed_start).bind(parsed_end)
            .fetch_all(&mysql_pool)
            .await.unwrap_or_default();

        let name = if let Some(c) = &map.custom_name { if c.is_empty() { map.original_name.clone() } else { c.clone() } } else { map.original_name.clone() };"""
        
    content = content.replace(old_target, new_logic)

    with open('src/lib.rs', 'w') as f:
        f.write(content)
else:
    print("Could not locate boundaries")

