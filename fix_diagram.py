import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# Change the filter to match either main_group OR sub_group
old_filter = "const groupSegments = segments.filter(s => s.main_group === calib.main_group);"
new_filter = "const groupSegments = segments.filter(s => s.main_group === calib.main_group || (s.sub_group && s.sub_group === calib.main_group));"

code = code.replace(old_filter, new_filter)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

