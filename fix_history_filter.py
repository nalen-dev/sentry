import re

with open('src-tauri/src/lib.rs', 'r') as f:
    lib = f.read()

# Replace temp >= 0.0 in get_groups_history
old_group = """                    let temp = r.TempAvg.unwrap_or(0) as f32 / 10.0;
                    if temp >= 0.0 {
                        group_data
                            .entry(seg.group.clone())
                            .or_default()
                            .entry(t_str)
                            .or_default()
                            .push(temp);
                    }"""
                    
new_group = """                    let temp = r.TempAvg.unwrap_or(0) as f32 / 10.0;
                    group_data
                        .entry(seg.group.clone())
                        .or_default()
                        .entry(t_str)
                        .or_default()
                        .push(temp);"""

lib = lib.replace(old_group, new_group)

# Replace temp >= 0.0 in get_segment_history
old_seg = """                    let temp = r.TempAvg.unwrap_or(0) as f32 / 10.0;
                    if temp >= 0.0 {
                        points.push(SegmentHistoryPoint {
                            time: ct.with_timezone(&chrono::Local).format("%H:%M").to_string(),
                            temp,
                        });
                    }"""
                    
new_seg = """                    let temp = r.TempAvg.unwrap_or(0) as f32 / 10.0;
                    points.push(SegmentHistoryPoint {
                        time: ct.with_timezone(&chrono::Local).format("%H:%M").to_string(),
                        temp,
                    });"""

lib = lib.replace(old_seg, new_seg)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(lib)

