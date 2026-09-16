import re

# 1. Update src-tauri/src/lib.rs
with open('src-tauri/src/lib.rs', 'r') as f:
    lib_code = f.read()

old_rust = """async fn update_segment_mapping(
    id: i32, 
    custom_name: Option<String>, 
    main_group: String, 
    sub_group: Option<String>,
    state: tauri::State<'_, SqlitePool>
) -> Result<(), String> {
    let _ = sqlx::query("UPDATE segment_mappings SET custom_name = ?, main_group = ?, sub_group = ? WHERE id = ?")
        .bind(custom_name)
        .bind(main_group)
        .bind(sub_group)
        .bind(id)"""

new_rust = """async fn update_segment_mapping(
    id: i32, 
    custom_name: Option<String>, 
    main_group: String, 
    start_m: Option<f64>,
    end_m: Option<f64>,
    state: tauri::State<'_, SqlitePool>
) -> Result<(), String> {
    let _ = sqlx::query("UPDATE segment_mappings SET custom_name = ?, main_group = ?, start_m = ?, end_m = ? WHERE id = ?")
        .bind(custom_name)
        .bind(main_group)
        .bind(start_m)
        .bind(end_m)
        .bind(id)"""

lib_code = lib_code.replace(old_rust, new_rust)
with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(lib_code)

# 2. Update src/pages/SettingPage.tsx
with open('src/pages/SettingPage.tsx', 'r') as f:
    set_code = f.read()

old_set = """  const handleUpdateBulkMapping = async (ids: number[], customName: string | null, mainGroup: string, subGroup: string | null) => {
    for (const id of ids) {
      await invoke('update_segment_mapping', {
        id,
        customName, // only applied if customName is provided (single select)
        mainGroup,
        subGroup
      });
    }"""
new_set = """  const handleUpdateBulkMapping = async (ids: number[], customName: string | null, mainGroup: string, startM: number | null, endM: number | null) => {
    for (const id of ids) {
      await invoke('update_segment_mapping', {
        id,
        customName,
        mainGroup,
        startM,
        endM
      });
    }"""
set_code = set_code.replace(old_set, new_set)
with open('src/pages/SettingPage.tsx', 'w') as f:
    f.write(set_code)

# 3. Update src/components/MappingGrid.tsx
with open('src/components/MappingGrid.tsx', 'r') as f:
    grid = f.read()

grid = grid.replace("onUpdateBulk: (ids: number[], customName: string | null, mainGroup: string, subGroup: string | null) => Promise<void>;", 
                    "onUpdateBulk: (ids: number[], customName: string | null, mainGroup: string, startM: number | null, endM: number | null) => Promise<void>;")

# Replace form state
grid = grid.replace("const [formSubGroup, setFormSubGroup] = useState('');", 
                    "const [formStartM, setFormStartM] = useState<number | ''>('');\n  const [formEndM, setFormEndM] = useState<number | ''>('');")

# Update useEffect
old_eff = """  React.useEffect(() => {
    if (selectedIds.size === 1) {
      const id = Array.from(selectedIds)[0];
      const mapping = mappings.find(m => m.id === id);
      if (mapping) {
        setFormMainGroup(mapping.main_group || 'Unassigned');
        setFormSubGroup(mapping.sub_group || '');
        setFormCustomName(mapping.custom_name || '');
      }
    } else {
      setFormMainGroup('Unassigned');
      setFormSubGroup('');
      setFormCustomName('');
    }
  }, [selectedIds, mappings]);"""

new_eff = """  React.useEffect(() => {
    if (selectedIds.size === 1) {
      const id = Array.from(selectedIds)[0];
      const mapping = mappings.find(m => m.id === id);
      if (mapping) {
        setFormMainGroup(mapping.main_group || 'Unassigned');
        setFormStartM(mapping.start_m ?? '');
        setFormEndM(mapping.end_m ?? '');
        setFormCustomName(mapping.custom_name || '');
      }
    } else {
      setFormMainGroup('Unassigned');
      setFormStartM('');
      setFormEndM('');
      setFormCustomName('');
    }
  }, [selectedIds, mappings]);"""
grid = grid.replace(old_eff, new_eff)

# Update handleSave
old_save = """  const handleSave = () => {
    onUpdateBulk(
      Array.from(selectedIds), 
      selectedIds.size === 1 ? formCustomName : null,
      formMainGroup,
      formSubGroup
    ).then(() => {
      showToast('Successfully updated mapping(s)', 'success');
      setSelectedIds(new Set());
    });
  };"""

new_save = """  const handleSave = () => {
    onUpdateBulk(
      Array.from(selectedIds), 
      selectedIds.size === 1 ? formCustomName : null,
      formMainGroup,
      formStartM === '' ? null : Number(formStartM),
      formEndM === '' ? null : Number(formEndM)
    ).then(() => {
      showToast('Successfully updated mapping(s)', 'success');
      setSelectedIds(new Set());
    });
  };"""
grid = grid.replace(old_save, new_save)

# Replace Sub Group input with Start M and End M, and update Options!
# Since my previous script failed to update options, I'll do it manually here.
old_form = """              <option value="Unassigned">Unassigned</option>
              <option value="BC4">BC4</option>
              <option value="BC5">BC5</option>
              <option value="Tunnel TCM">Tunnel TCM</option>
              <option value="Tunnel BEK">Tunnel BEK</option>
            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-bold text-text-secondary uppercase tracking-wider block">Sub Group (Optional)</label>
            <input 
              type="text" 
              value={formSubGroup} 
              onChange={e => setFormSubGroup(e.target.value)}
              disabled={selectedIds.size === 0}
              placeholder="e.g. Zone A"
              className="w-full bg-bg-panel border border-border rounded-lg p-2 text-sm text-text-primary focus:outline-none focus:border-scada-primary disabled:opacity-50"
            />
          </div>"""

# Fallback just in case old_form was modified somehow
import re
grid = re.sub(r'<option value="Unassigned">Unassigned</option>.*?</select>\s*</div>\s*<div className="space-y-1\.5">\s*<label[^>]*>Sub Group \(Optional\)</label>\s*<input[^>]*value=\{formSubGroup\}[^>]*/>\s*</div>', 
              """<option value="Unassigned">Unassigned</option>
              <option value="BC4 A">BC4 A</option>
              <option value="BC4 B">BC4 B</option>
              <option value="BC5">BC5</option>
              <option value="BC45-MOTOR">BC45-MOTOR</option>
              <option value="BEK56">BEK56</option>
              <option value="BEK34">BEK34</option>
              <option value="TCM16">TCM16</option>
            </select>
          </div>

          <div className="flex space-x-2">
            <div className="space-y-1.5 flex-1">
              <label className="text-[10px] font-bold text-text-secondary uppercase tracking-wider block">Start (M)</label>
              <input 
                type="number" 
                value={formStartM}
                onChange={e => setFormStartM(e.target.value === '' ? '' : Number(e.target.value))}
                disabled={selectedIds.size === 0}
                placeholder="0"
                className="w-full bg-bg-panel border border-border rounded-lg p-2 text-sm text-text-primary focus:outline-none focus:border-scada-primary disabled:opacity-50"
              />
            </div>
            <div className="space-y-1.5 flex-1">
              <label className="text-[10px] font-bold text-text-secondary uppercase tracking-wider block">End (M)</label>
              <input 
                type="number" 
                value={formEndM}
                onChange={e => setFormEndM(e.target.value === '' ? '' : Number(e.target.value))}
                disabled={selectedIds.size === 0}
                placeholder="50"
                className="w-full bg-bg-panel border border-border rounded-lg p-2 text-sm text-text-primary focus:outline-none focus:border-scada-primary disabled:opacity-50"
              />
            </div>
          </div>""", grid, flags=re.DOTALL)


# Write grid back
with open('src/components/MappingGrid.tsx', 'w') as f:
    f.write(grid)

