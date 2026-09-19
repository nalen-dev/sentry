import re

with open('src/components/MappingGrid.tsx', 'r') as f:
    code = f.read()

old_use_effect = """  // Sync form when selection changes (if 1 selected)
  React.useEffect(() => {
    if (selectedIds.size === 1) {
      const id = Array.from(selectedIds)[0];
      const map = mappings.find(m => m.id === id);
      if (map) {
        setFormMainGroup(map.main_group || 'Unassigned');
        setFormSubGroup(map.sub_group || '');
        setFormStartM(map.start_m !== null && map.start_m !== undefined ? map.start_m : '');
        setFormEndM(map.end_m !== null && map.end_m !== undefined ? map.end_m : '');
        setFormCustomName(map.custom_name || '');
      }
    } else {
      setFormSubGroup('');
      setFormStartM('');
      setFormEndM('');
      setFormCustomName('');
    }
  }, [selectedIds, mappings]);"""

new_use_effect = """  // Sync form when selection changes
  React.useEffect(() => {
    if (selectedIds.size > 0) {
      const selected = mappings.filter(m => selectedIds.has(m.id));
      
      // Check if all selected share the same properties
      const allSameMain = selected.every(m => m.main_group === selected[0].main_group);
      const allSameSub = selected.every(m => m.sub_group === selected[0].sub_group);
      
      setFormMainGroup(allSameMain ? (selected[0].main_group || 'Unassigned') : 'Unassigned');
      setFormSubGroup(allSameSub ? (selected[0].sub_group || '') : '');
      
      if (selectedIds.size === 1) {
        setFormStartM(selected[0].start_m !== null && selected[0].start_m !== undefined ? selected[0].start_m : '');
        setFormEndM(selected[0].end_m !== null && selected[0].end_m !== undefined ? selected[0].end_m : '');
        setFormCustomName(selected[0].custom_name || '');
      } else {
        setFormStartM('');
        setFormEndM('');
        setFormCustomName('');
      }
    } else {
      setFormSubGroup('');
      setFormStartM('');
      setFormEndM('');
      setFormCustomName('');
    }
  }, [selectedIds, mappings]);"""

code = code.replace(old_use_effect, new_use_effect)

# Update handleSave to only pass form fields if they are not explicitly meant to be ignored.
# Wait, handleSave will currently send formSubGroup === '' ? null : formSubGroup. 
# If they are mixed (''), it will send null and overwrite! We should probably let it send null so they can clear subgroups bulk.
# But we need a way to tell handleSave: "Don't update this field".
# Actually, standard behavior: if you bulk edit and leave it blank, it clears it. This is standard and acceptable if they can see it's blank.

with open('src/components/MappingGrid.tsx', 'w') as f:
    f.write(code)

