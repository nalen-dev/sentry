import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    content = f.read()

# Replace the skip logic
skip_logic_old = """        const startM = seg.start_m || 0;
        const endM = seg.end_m || 0;
        if (startM === endM) return null;

        const totalM = calib.end_m - calib.start_m;
        if (totalM === 0) return null;"""

skip_logic_new = """        let startM = seg.start_m || 0;
        let endM = seg.end_m || 0;
        
        const totalM = calib.end_m - calib.start_m;
        if (totalM === 0) return null;
        
        // Fallback: If segment has no distance mapping, assume it covers the whole group
        if (startM === endM) {
            startM = calib.start_m;
            endM = calib.end_m;
        }"""

content = content.replace(skip_logic_old, skip_logic_new)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(content)

