import re

# 1. Update MapVisualization.tsx
with open('src/features/map/MapVisualization.tsx', 'r') as f:
    code = f.read()

# Replace all green (#43b581) with blue (#3b82f6)
code = code.replace("#43b581", "#3b82f6")

with open('src/features/map/MapVisualization.tsx', 'w') as f:
    f.write(code)

# 2. Update index.css
with open('src/index.css', 'r') as f:
    css = f.read()

# Replace tooltip colors
css = css.replace("color: #43b581 !important; border-color: rgba(67, 181, 129, 0.3)", "color: #3b82f6 !important; border-color: rgba(59, 130, 246, 0.3)")

with open('src/index.css', 'w') as f:
    f.write(css)

