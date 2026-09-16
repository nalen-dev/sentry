import re

# 1. Update MappingGrid.tsx
with open('src/components/MappingGrid.tsx', 'r') as f:
    grid = f.read()

# Add subGroup to onUpdateBulk props
grid = grid.replace("onUpdateBulk: (ids: number[], customName: string | null, mainGroup: string, startM: number | null, endM: number | null) => Promise<void>;",
                    "onUpdateBulk: (ids: number[], customName: string | null, mainGroup: string, subGroup: string | null, startM: number | null, endM: number | null) => Promise<void>;")

# Add form state
grid = grid.replace("const [formMainGroup, setFormMainGroup] = useState('Unassigned');",
                    "const [formMainGroup, setFormMainGroup] = useState('Unassigned');\n  const [formSubGroup, setFormSubGroup] = useState('');")

# Update useEffect
old_eff = """        setFormMainGroup(mapping.main_group || 'Unassigned');
        setFormStartM(mapping.start_m ?? '');
        setFormEndM(mapping.end_m ?? '');
        setFormCustomName(mapping.custom_name || '');
      }
    } else {
      setFormMainGroup('Unassigned');
      setFormStartM('');
      setFormEndM('');
      setFormCustomName('');
    }"""
new_eff = """        setFormMainGroup(mapping.main_group || 'Unassigned');
        setFormSubGroup(mapping.sub_group || '');
        setFormStartM(mapping.start_m ?? '');
        setFormEndM(mapping.end_m ?? '');
        setFormCustomName(mapping.custom_name || '');
      }
    } else {
      setFormMainGroup('Unassigned');
      setFormSubGroup('');
      setFormStartM('');
      setFormEndM('');
      setFormCustomName('');
    }"""
grid = grid.replace(old_eff, new_eff)

# Update handleSave
old_save = """    onUpdateBulk(
      Array.from(selectedIds), 
      selectedIds.size === 1 ? formCustomName : null,
      formMainGroup,
      formStartM === '' ? null : Number(formStartM),
      formEndM === '' ? null : Number(formEndM)
    )"""
new_save = """    onUpdateBulk(
      Array.from(selectedIds), 
      selectedIds.size === 1 ? formCustomName : null,
      formMainGroup,
      formSubGroup === '' ? null : formSubGroup,
      formStartM === '' ? null : Number(formStartM),
      formEndM === '' ? null : Number(formEndM)
    )"""
grid = grid.replace(old_save, new_save)

# Re-insert Sub Group input in the UI
old_input = """            </select>
          </div>

          <div className="flex space-x-2">"""
new_input = """            </select>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-bold text-text-secondary uppercase tracking-wider block">Sub Group (Optional)</label>
            <input 
              type="text" 
              value={formSubGroup}
              onChange={e => setFormSubGroup(e.target.value)}
              disabled={selectedIds.size === 0}
              placeholder="e.g. TN1-2"
              className="w-full bg-bg-panel border border-border rounded-lg p-2 text-sm text-text-primary focus:outline-none focus:border-scada-primary disabled:opacity-50"
            />
          </div>

          <div className="flex space-x-2">"""
grid = grid.replace(old_input, new_input)

# Update Badge to show Sub Group again
grid = grid.replace("{mapping.main_group}", "{mapping.main_group}{mapping.sub_group ? ` - ${mapping.sub_group}` : ''}")

with open('src/components/MappingGrid.tsx', 'w') as f:
    f.write(grid)


# 2. Update SettingPage.tsx
with open('src/pages/SettingPage.tsx', 'r') as f:
    set_code = f.read()

set_code = set_code.replace("const handleUpdateBulkMapping = async (ids: number[], customName: string | null, mainGroup: string, startM: number | null, endM: number | null) => {",
                            "const handleUpdateBulkMapping = async (ids: number[], customName: string | null, mainGroup: string, subGroup: string | null, startM: number | null, endM: number | null) => {")
set_code = set_code.replace("mainGroup,\n        startM,\n        endM", "mainGroup,\n        subGroup,\n        startM,\n        endM")

with open('src/pages/SettingPage.tsx', 'w') as f:
    f.write(set_code)


# 3. Update lib.rs
with open('src-tauri/src/lib.rs', 'r') as f:
    lib_code = f.read()

old_rust = """async fn update_segment_mapping(
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

new_rust = """async fn update_segment_mapping(
    id: i32, 
    custom_name: Option<String>, 
    main_group: String,
    sub_group: Option<String>,
    start_m: Option<f64>,
    end_m: Option<f64>,
    state: tauri::State<'_, SqlitePool>
) -> Result<(), String> {
    let _ = sqlx::query("UPDATE segment_mappings SET custom_name = ?, main_group = ?, sub_group = ?, start_m = ?, end_m = ? WHERE id = ?")
        .bind(custom_name)
        .bind(main_group)
        .bind(sub_group)
        .bind(start_m)
        .bind(end_m)
        .bind(id)"""

lib_code = lib_code.replace(old_rust, new_rust)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(lib_code)

