import re

with open('src/lib.rs', 'r') as f:
    content = f.read()

# 1. get_segment_curve
curve_old = """                for s in string_parts {
                    if let Ok(v) = s.parse::<i32>() {
                        curve.push(CurvePoint { distance: dist, temp: v as f32 / 10.0 });
                        dist += 1;
                    }
                }"""
curve_new = """                for s in string_parts {
                    if let Ok(v) = s.parse::<i32>() {
                        let temp = v as f32 / 10.0;
                        // Filter out error values like -327.7
                        if temp > -100.0 {
                            curve.push(CurvePoint { distance: dist, temp });
                        }
                        dist += 1;
                    }
                }"""
content = content.replace(curve_old, curve_new)

# 2. get_groups_history
hist_old = """                let temp = r.TempAvg.unwrap_or(0) as f32 / 10.0;
                
                group_data
                    .entry(map.main_group.clone())
                    .or_default()
                    .entry(t_str)
                    .or_default()
                    .push(temp);"""
hist_new = """                let temp = r.TempAvg.unwrap_or(0) as f32 / 10.0;
                if temp > -100.0 {
                    group_data
                        .entry(map.main_group.clone())
                        .or_default()
                        .entry(t_str)
                        .or_default()
                        .push(temp);
                }"""
content = content.replace(hist_old, hist_new)

# 3. get_live_segments
live_old = """            results.push(LiveSegment {
                id: map.id,
                dts_ch: map.dts_ch,
                dts_code: map.dts_code,
                name: map.custom_name.unwrap_or(map.original_name),
                main_group: map.main_group,
                sub_group: map.sub_group,
                temp_avg: l.temp_avg.unwrap_or(0) as f32 / 10.0,
                temp_min: l.temp_min.unwrap_or(0) as f32 / 10.0,
                temp_max: l.temp_max.unwrap_or(0) as f32 / 10.0,
                temp_min_p: l.temp_min_p.unwrap_or(0),
                temp_max_p: l.temp_max_p.unwrap_or(0),
            });"""
live_new = """            let avg = l.temp_avg.unwrap_or(0) as f32 / 10.0;
            let min = l.temp_min.unwrap_or(0) as f32 / 10.0;
            let max = l.temp_max.unwrap_or(0) as f32 / 10.0;
            results.push(LiveSegment {
                id: map.id,
                dts_ch: map.dts_ch,
                dts_code: map.dts_code,
                name: map.custom_name.unwrap_or(map.original_name),
                main_group: map.main_group,
                sub_group: map.sub_group,
                temp_avg: if avg > -100.0 { avg } else { 0.0 },
                temp_min: if min > -100.0 { min } else { 0.0 },
                temp_max: if max > -100.0 { max } else { 0.0 },
                temp_min_p: l.temp_min_p.unwrap_or(0),
                temp_max_p: l.temp_max_p.unwrap_or(0),
            });"""
content = content.replace(live_old, live_new)


with open('src/lib.rs', 'w') as f:
    f.write(content)

