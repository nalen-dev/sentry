import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

old_fallback = """        } else {
          // Standard straight line interpolation for non-poly paths (e.g. BC4 A, BC4 B)
          const x1 = calib.start_svg_x + r1 * (calib.end_svg_x - calib.start_svg_x);"""

new_fallback = """        } else {
          // Prevent drawing the old buggy fallback straight lines for groups that are now handled strictly by subgroup polylines
          if (['TCM16', 'BEK56', 'BEK34'].includes(calib.main_group)) return null;

          // Standard straight line interpolation for non-poly paths (e.g. BC4 A, BC4 B)
          const x1 = calib.start_svg_x + r1 * (calib.end_svg_x - calib.start_svg_x);"""

code = code.replace(old_fallback, new_fallback)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

