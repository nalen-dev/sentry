import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# Reverse the arrays so that 0m is at the Control Room (or the side closer to it)
old_paths = """  // Hardcoded polylines for exact physical loops
  const SUBGROUP_PATHS: Record<string, number[][]> = {
    // TCM16 Loops (Starts from bottom of tunnel)
    'TN12': [[60, 372], [60, 314], [130, 314], [130, 372]],
    'TN23': [[130, 372], [130, 314], [200, 314], [200, 372]],
    'TN34': [[200, 372], [200, 314], [270, 314], [270, 372]],
    'TN45': [[270, 372], [270, 314], [340, 314], [340, 372]], // Added TN45 just in case
    'TN56': [[340, 372], [340, 314], [410, 314], [410, 372]],
    'TN6CR': [[410, 372], [410, 314], [513, 314], [513, 360]], // Connected down to Control Room

    // BEK34 Loops
    'BE34M': [[235, 220], [235, 282], [305, 282], [305, 220]],
    'BEK4CR': [[305, 220], [305, 282], [513, 282], [513, 360]],

    // BEK56 Loops
    'BEK56M': [[375, 220], [375, 274], [445, 274], [445, 220]],
    'BEK6CR': [[445, 220], [445, 274], [513, 274], [513, 360]]
  };"""

new_paths = """  // Hardcoded polylines for exact physical loops. 
  // Arrays are reversed so that index 0 is always the side CLOSER to the Control Room (0 meters).
  const SUBGROUP_PATHS: Record<string, number[][]> = {
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

code = code.replace(old_paths, new_paths)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

