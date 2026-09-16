import re

with open('src/components/MappingGrid.tsx', 'r') as f:
    grid = f.read()

# 1. Clean up unused formSubGroup state if it exists (it doesn't, because we replaced it with formStartM)
# 2. Fix the TS errors: setFormSubGroup is still being called inside handleToggleArea and handleToggleChannel? No! It's in the select all toggle?
# Let's see where setFormSubGroup is.
# Wait, let's just completely replace the RIGHT: EDITOR PANEL section from <div className="space-y-1.5"> up to the end of the form.

editor_panel_old = """          <div className="space-y-1.5">
            <label className="text-xs font-bold text-text-secondary uppercase tracking-wider block">Main Group</label>
            <select 
              value={formMainGroup}
              onChange={e => setFormMainGroup(e.target.value)}
              disabled={selectedIds.size === 0}
              className="w-full bg-bg-panel border border-border rounded-lg p-2 text-sm text-text-primary focus:outline-none focus:border-scada-primary disabled:opacity-50"
            >
              <option value="Unassigned">Unassigned</option>
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
              placeholder="e.g. TCM 1"
              className="w-full bg-bg-panel border border-border rounded-lg p-2 text-sm text-text-primary focus:outline-none focus:border-scada-primary disabled:opacity-50"
            />
          </div>"""

editor_panel_new = """          <div className="space-y-1.5">
            <label className="text-xs font-bold text-text-secondary uppercase tracking-wider block">Main Group</label>
            <select 
              value={formMainGroup}
              onChange={e => setFormMainGroup(e.target.value)}
              disabled={selectedIds.size === 0}
              className="w-full bg-bg-panel border border-border rounded-lg p-2 text-sm text-text-primary focus:outline-none focus:border-scada-primary disabled:opacity-50"
            >
              <option value="Unassigned">Unassigned</option>
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
              <label className="text-xs font-bold text-text-secondary uppercase tracking-wider block">Start (M)</label>
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
              <label className="text-xs font-bold text-text-secondary uppercase tracking-wider block">End (M)</label>
              <input 
                type="number" 
                value={formEndM}
                onChange={e => setFormEndM(e.target.value === '' ? '' : Number(e.target.value))}
                disabled={selectedIds.size === 0}
                placeholder="50"
                className="w-full bg-bg-panel border border-border rounded-lg p-2 text-sm text-text-primary focus:outline-none focus:border-scada-primary disabled:opacity-50"
              />
            </div>
          </div>"""

grid = grid.replace(editor_panel_old, editor_panel_new)

# Also fix the formSubGroup in quick select toggle if it exists there
grid = grid.replace("setFormSubGroup(selected.sub_group || '');", "setFormStartM(selected.start_m ?? '');\n        setFormEndM(selected.end_m ?? '');")
grid = grid.replace("formSubGroup || null", "formStartM === '' ? null : Number(formStartM), formEndM === '' ? null : Number(formEndM)")

# And just in case there's another setFormSubGroup call:
grid = grid.replace("setFormSubGroup('');", "setFormStartM('');\n      setFormEndM('');")

with open('src/components/MappingGrid.tsx', 'w') as f:
    f.write(grid)

