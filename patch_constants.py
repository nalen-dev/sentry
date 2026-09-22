import re

with open('src/data/constants.ts', 'r') as f:
    content = f.read()

colors_injection = """
// Fixed global palette to ensure consistency between Map and Chart
export const GROUP_COLORS: Record<string, string> = {
  'BC4 A': '#06b6d4',      // Cyan
  'TCM16': '#10b981',      // Green
  'BEK34': '#a855f7',      // Purple
  'BEK56': '#f97316',      // Orange
  'BC4 B': '#ec4899',      // Pink
  'BC5': '#3b82f6',        // Blue
  'BC45-MOTOR': '#8b5cf6', // Violet
};

export const CHART_COLORS_FALLBACK = ['#06b6d4', '#10b981', '#a855f7', '#f97316', '#ec4899', '#3b82f6', '#8b5cf6'];
"""

if "GROUP_COLORS" not in content:
    content += colors_injection

with open('src/data/constants.ts', 'w') as f:
    f.write(content)

