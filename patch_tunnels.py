import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# Replace the SUBGROUP_PATHS completely
old_subgroup = """const SUBGROUP_PATHS: Record<string, number[][]> = {
    // TCM16 Loops (0m at Control Room)
    'TN6CR': [[513, 360], [513, 314], [410, 314], [410, 372]], // Control Room to TN6 bottom
    'TN56': [[410, 372], [410, 314], [340, 314], [340, 372]],  // TN6 bottom to TN5 bottom
    'TN45': [[340, 372], [340, 314], [270, 314], [270, 372]],  // TN5 bottom to TN4 bottom
    'TN34': [[270, 372], [270, 314], [200, 314], [200, 372]],  // TN4 bottom to TN3 bottom
    'TN23': [[200, 372], [200, 314], [130, 314], [130, 372]],  // TN3 bottom to TN2 bottom
    'TN12': [[130, 372], [130, 314], [60, 314], [60, 372]],    // TN2 bottom to TN1 bottom

    // BEK34 Loops (0m at Control Room)
    'BEK4CR': [[513, 360], [513, 282], [305, 282], [305, 220]], // Control Room to BEK4 bottom
    'BE34M': [[305, 220], [305, 282], [235, 282], [235, 220]],  // BEK4 bottom to BEK3 bottom

    // BEK56 Loops (0m at Control Room)
    'BEK6CR': [[513, 360], [513, 274], [445, 274], [445, 220]], // Control Room to BEK6 bottom
    'BEK56M': [[445, 220], [445, 274], [375, 274], [375, 220]]  // BEK6 bottom to BEK5 bottom
  };"""

new_subgroup = """const SUBGROUP_PATHS: Record<string, number[][]> = {
    // TCM16 Groups (Left to Right per user specs: Horizontal -> Loop -> Next Horizontal)
    'TN12': [[60, 314], [60, 372], [60, 314], [130, 314]],
    'TN23': [[130, 314], [130, 372], [130, 314], [200, 314]],
    'TN34': [[200, 314], [200, 372], [200, 314], [270, 314]],
    'TN45': [[270, 314], [270, 372], [270, 314], [340, 314]],
    'TN56': [[340, 314], [340, 372], [340, 314], [410, 314]],
    'TN6CR': [[410, 314], [410, 372], [410, 314], [513, 314], [513, 360]],

    // BEK34 Groups (Right to Left: CR -> BEK4 -> BEK3)
    'BEK4CR': [[513, 360], [513, 282], [305, 282]], 
    'BE34M': [[305, 282], [305, 220], [305, 282], [235, 282], [235, 220]],

    // BEK56 Groups (Right to Left: CR -> BEK6 -> BEK5)
    'BEK6CR': [[513, 360], [513, 274], [445, 274]], 
    'BEK56M': [[445, 274], [445, 220], [445, 274], [375, 274], [375, 220]]
  };"""

code = code.replace(old_subgroup, new_subgroup)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

