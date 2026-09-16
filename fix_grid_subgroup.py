import re

with open('src/components/MappingGrid.tsx', 'r') as f:
    code = f.read()

old_click = """      const selected = mappings.find(m => m.id === Array.from(newSet)[0]);
      if (selected) {
        setFormMainGroup(selected.main_group || 'Unassigned');
        setFormStartM(selected.start_m ?? '');
        setFormEndM(selected.end_m ?? '');
        setFormCustomName(selected.custom_name || '');
      }"""

new_click = """      const selected = mappings.find(m => m.id === Array.from(newSet)[0]);
      if (selected) {
        setFormMainGroup(selected.main_group || 'Unassigned');
        setFormSubGroup(selected.sub_group || '');
        setFormStartM(selected.start_m ?? '');
        setFormEndM(selected.end_m ?? '');
        setFormCustomName(selected.custom_name || '');
      }"""

code = code.replace(old_click, new_click)

with open('src/components/MappingGrid.tsx', 'w') as f:
    f.write(code)

