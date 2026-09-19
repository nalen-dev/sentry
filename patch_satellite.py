import re

# 1. Update MapVisualization.tsx
with open('src/features/map/MapVisualization.tsx', 'r') as f:
    code = f.read()

# Replace CABLE B
code = code.replace("pathOptions={{ color: '#eab308', weight: 3 }}", "pathOptions={{ color: '#43b581', weight: 3 }}")
code = code.replace("<Tooltip sticky>CABLE B - Warning</Tooltip>", "<Tooltip sticky>CABLE B</Tooltip>")

# Replace CABLE C
code = code.replace("pathOptions={{ color: '#f04747', weight: 3, className: 'animate-pulse' }}", "pathOptions={{ color: '#43b581', weight: 3 }}")
code = code.replace("<Tooltip sticky>CABLE C - Danger (Overheat)</Tooltip>", "<Tooltip sticky>CABLE C</Tooltip>")

# Replace CABLE A and D Tooltips just in case they have extra text
code = code.replace("<Tooltip sticky>CABLE A - Normal</Tooltip>", "<Tooltip sticky>CABLE A</Tooltip>")
code = code.replace("<Tooltip sticky>CABLE D - Normal</Tooltip>", "<Tooltip sticky>CABLE D</Tooltip>")

with open('src/features/map/MapVisualization.tsx', 'w') as f:
    f.write(code)

# 2. Update index.css
with open('src/index.css', 'r') as f:
    css = f.read()

css = css.replace(".custom-tunnel-tooltip.fo-b { color: #eab308 !important; border-color: rgba(234, 179, 8, 0.3) !important; }", ".custom-tunnel-tooltip.fo-b { color: #43b581 !important; border-color: rgba(67, 181, 129, 0.3) !important; }")

with open('src/index.css', 'w') as f:
    f.write(css)

