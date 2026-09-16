import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    code = f.read()

# Let's insert the smart naming logic before we map to Area objects.
logic = """
  // Smart Naming Algorithm
  const groupedSegments: Record<string, LiveSegment[]> = {};
  data.forEach(m => {
    if (m.main_group && m.main_group !== 'Unassigned') {
      if (!groupedSegments[m.main_group]) groupedSegments[m.main_group] = [];
      groupedSegments[m.main_group].push(m);
    }
  });

  Object.keys(groupedSegments).forEach(group => {
    groupedSegments[group].sort((a, b) => (a.start_m || 0) - (b.start_m || 0));
    groupedSegments[group].forEach((m, index) => {
      // Create a smart name
      const prefix = m.sub_group ? m.sub_group : m.main_group;
      (m as any).smart_name = `${prefix} - ${index + 1}`;
    });
  });

  const processedData = data.map(m => {
"""

old_map_start = "const processedData = data.map(m => {"

code = code.replace(old_map_start, logic)

# Replace the name assignment
old_name = "name: m.custom_name || m.original_name,"
new_name = "name: (m as any).smart_name || m.custom_name || m.original_name,"

code = code.replace(old_name, new_name)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(code)

