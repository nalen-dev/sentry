import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    code = f.read()

old_logic = """
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
  });"""

new_logic = """
  // Smart Naming Algorithm
  const groupedSegments: Record<string, LiveSegment[]> = {};
  data.forEach(m => {
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
  });"""

code = code.replace(old_logic, new_logic)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(code)

