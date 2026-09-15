import re

with open('src-tauri/src/lib.rs', 'r') as f:
    lib = f.read()

# Replace avg with max in get_groups_history
old_agg = """        for (g_name, times_map) in &group_data {
            if let Some(temps) = times_map.get(&t) {
                let sum: f32 = temps.iter().sum();
                let avg = sum / temps.len() as f32;
                groups_map.insert(g_name.clone(), avg);
            }
        }"""
        
new_agg = """        for (g_name, times_map) in &group_data {
            if let Some(temps) = times_map.get(&t) {
                let max_temp = temps.iter().copied().fold(f32::NEG_INFINITY, f32::max);
                groups_map.insert(g_name.clone(), max_temp);
            }
        }"""

lib = lib.replace(old_agg, new_agg)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(lib)

