import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# Fix TN6CR / TCM6CR
code = code.replace("'TN6CR': [[513, 360], [513, 314], [410, 314], [410, 372], [410, 314]],", "'TN6CR': [[513, 314], [410, 314], [410, 372], [410, 314]],")
code = code.replace("'TCM6CR': [[513, 360], [513, 314], [410, 314], [410, 372], [410, 314]],", "'TCM6CR': [[513, 314], [410, 314], [410, 372], [410, 314]],")

# Fix BEK4CR
code = code.replace("'BEK4CR': [[513, 360], [513, 282], [305, 282]],", "'BEK4CR': [[513, 282], [305, 282]],")

# Fix BEK6CR
code = code.replace("'BEK6CR': [[513, 360], [513, 274], [445, 274]],", "'BEK6CR': [[513, 274], [445, 274]],")

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

