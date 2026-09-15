import re

with open('src-tauri/src/lib.rs', 'r') as f:
    content = f.read()

# Fix get_groups_history time format
hist_old = 'let t_str = ct.format("%H:%M").to_string();'
hist_new = 'let t_str = ct.with_timezone(&chrono::Local).format("%H:%M").to_string();'
content = content.replace(hist_old, hist_new)

# Fix get_alarms time format
alarms_old = 'let t = r.CreationTime.map(|ct| ct.format("%H:%M:%S").to_string()).unwrap_or_default();'
alarms_new = 'let t = r.CreationTime.map(|ct| ct.with_timezone(&chrono::Local).format("%H:%M:%S").to_string()).unwrap_or_default();'
content = content.replace(alarms_old, alarms_new)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(content)

