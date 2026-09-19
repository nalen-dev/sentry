import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    code = f.read()

logic = """
  // Smart Naming Algorithm
  const groupedSegments: Record<string, LiveSegment[]> = {};
  mappings.forEach(m => {
    if (m.main_group && m.main_group !== 'Unassigned') {
      const prefix = m.sub_group ? m.sub_group : m.main_group;
      if (!groupedSegments[prefix]) groupedSegments[prefix] = [];
      groupedSegments[prefix].push(m);
    }
  });

  Object.keys(groupedSegments).forEach(prefix => {
    groupedSegments[prefix].sort((a, b) => (a.start_m || 0) - (b.start_m || 0));
    groupedSegments[prefix].forEach((m, index) => {
      (m as any).smart_name = `${prefix} - ${index + 1}`;
    });
  });

  const baseAreas: (SegmentData & { mainGroup: string; subGroup?: string })[] = mappings.map(m => {"""

old_map = "const baseAreas: (SegmentData & { mainGroup: string; subGroup?: string })[] = mappings.map(m => {"

code = code.replace(old_map, logic)

old_name = "name: m.custom_name || m.original_name,"
new_name = "name: (m as any).smart_name || m.custom_name || m.original_name,"

code = code.replace(old_name, new_name)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(code)

