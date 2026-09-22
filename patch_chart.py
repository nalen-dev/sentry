import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    content = f.read()

# Add import
content = content.replace("import { invoke } from '@tauri-apps/api/core';", "import { invoke } from '@tauri-apps/api/core';\nimport { GROUP_COLORS, CHART_COLORS_FALLBACK } from '../data/constants';")

# Remove old COLORS
content = re.sub(r"const COLORS = \['#06b6d4'.*?\];\n", "", content)

# Replace COLORS[i % COLORS.length] with the mapping
content = content.replace("stroke={COLORS[i % COLORS.length]}", "stroke={GROUP_COLORS[name] || CHART_COLORS_FALLBACK[i % CHART_COLORS_FALLBACK.length]}")

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(content)

