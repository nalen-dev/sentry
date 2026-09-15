import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    content = f.read()

# Fix the arguments back to camelCase as expected by Tauri's default mapper
content = content.replace(
    "invoke('get_segment_curve', { dts_ch: ch, start_m: safeMin, end_m: safeMax })",
    "invoke('get_segment_curve', { dtsCh: ch, startM: safeMin, endM: safeMax })"
)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(content)

