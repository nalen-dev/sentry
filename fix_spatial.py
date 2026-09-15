import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    content = f.read()

# Fix Tauri command args
content = content.replace("invoke('get_segment_curve', { dtsCh: ch })", "invoke('get_segment_curve', { dts_ch: ch })")

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(content)

with open('src-tauri/src/lib.rs', 'r') as f:
    lib = f.read()

# Fix temperatures
lib = lib.replace("if temp > -100.0 {", "if temp >= 0.0 {")
lib = lib.replace("if avg > -100.0 { avg } else { 0.0 }", "if avg >= 0.0 { avg } else { 0.0 }")
lib = lib.replace("if min > -100.0 { min } else { 0.0 }", "if min >= 0.0 { min } else { 0.0 }")
lib = lib.replace("if max > -100.0 { max } else { 0.0 }", "if max >= 0.0 { max } else { 0.0 }")

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(lib)

