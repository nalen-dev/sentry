import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

old_interface = """interface LiveSegment {
  main_group: string;
  start_m?: number | null;
  end_m?: number | null;
  temp_max: number;
  temp_avg: number;
}"""

new_interface = """interface LiveSegment {
  main_group: string;
  sub_group?: string | null;
  start_m?: number | null;
  end_m?: number | null;
  temp_max: number;
  temp_avg: number;
}"""

code = code.replace(old_interface, new_interface)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

