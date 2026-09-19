import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

old_paths = """  const SUBGROUP_PATHS: Record<string, number[][]> = {
    // TCM16 Groups (Left to Right per user specs: Horizontal -> Loop -> Next Horizontal)
    'TN12': [[60, 314], [60, 372], [60, 314], [130, 314]],
    'TN23': [[130, 314], [130, 372], [130, 314], [200, 314]],
    'TN34': [[200, 314], [200, 372], [200, 314], [270, 314]],
    'TN45': [[270, 314], [270, 372], [270, 314], [340, 314]],
    'TN56': [[340, 314], [340, 372], [340, 314], [410, 314]],
    'TN6CR': [[410, 314], [410, 372], [410, 314], [513, 314], [513, 360]],
    'TCM6CR': [[410, 314], [410, 372], [410, 314], [513, 314], [513, 360]],"""

new_paths = """  const SUBGROUP_PATHS: Record<string, number[][]> = {
    // TCM16 Groups (Right to Left: 0m is at Control Room, so fiber travels CR -> TCM6 -> TCM5 ...)
    'TN12': [[130, 314], [60, 314], [60, 372], [60, 314]],
    'TN23': [[200, 314], [130, 314], [130, 372], [130, 314]],
    'TN34': [[270, 314], [200, 314], [200, 372], [200, 314]],
    'TN45': [[340, 314], [270, 314], [270, 372], [270, 314]],
    'TN56': [[410, 314], [340, 314], [340, 372], [340, 314]],
    'TN6CR': [[513, 360], [513, 314], [410, 314], [410, 372], [410, 314]],
    'TCM6CR': [[513, 360], [513, 314], [410, 314], [410, 372], [410, 314]],"""

code = code.replace(old_paths, new_paths)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

