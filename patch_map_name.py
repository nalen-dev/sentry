import re

with open('src/features/map/MapVisualization.tsx', 'r') as f:
    content = f.read()

# Replace the name logic
old_name = "name: criticalSegment.custom_name || criticalSegment.original_name || `${groupName} Hotspot`,"
new_name = "name: (criticalSegment as any).smart_name || criticalSegment.custom_name || criticalSegment.original_name || `${groupName} Hotspot`,"

content = content.replace(old_name, new_name)

with open('src/features/map/MapVisualization.tsx', 'w') as f:
    f.write(content)

