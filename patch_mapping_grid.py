import re

with open('src/components/MappingGrid.tsx', 'r') as f:
    code = f.read()

use_effect_insertion = """  // Form states
  const [formMainGroup, setFormMainGroup] = useState('Unassigned');
  const [formSubGroup, setFormSubGroup] = useState('');
  const [formStartM, setFormStartM] = useState<number | ''>('');
  const [formEndM, setFormEndM] = useState<number | ''>('');
  const [formCustomName, setFormCustomName] = useState('');

  // Sync form when selection changes (if 1 selected)
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

code = code.replace("""  // Form states
  const [formMainGroup, setFormMainGroup] = useState('Unassigned');
  const [formSubGroup, setFormSubGroup] = useState('');
  const [formStartM, setFormStartM] = useState<number | ''>('');
  const [formEndM, setFormEndM] = useState<number | ''>('');
  const [formCustomName, setFormCustomName] = useState('');""", use_effect_insertion)

with open('src/components/MappingGrid.tsx', 'w') as f:
    f.write(code)

