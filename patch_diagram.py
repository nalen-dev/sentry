import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

target = """interface MapCalibration {
  main_group: string;
  start_m: number;
  end_m: number;
  start_svg_x: number;
  start_svg_y: number;
  end_svg_x: number;
  end_svg_y: number;
}"""

replacement = """interface MapCalibration {
  main_group: string;
  sub_group?: string;
  start_m: number;
  end_m: number;
  start_svg_x: number;
  start_svg_y: number;
  end_svg_x: number;
  end_svg_y: number;
}"""

code = code.replace(target, replacement)
code = code.replace("SUBGROUP_PATHS[calib.main_group]", "SUBGROUP_PATHS[calib.sub_group || '']")

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

