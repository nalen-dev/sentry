import re

with open('src/components/MappingGrid.tsx', 'r') as f:
    code = f.read()

# Replace Group Colors
old_colors = """  const groupColors: Record<string, string> = {
    'Unassigned': 'bg-bg-panel border-border',
    'BC4': 'bg-blue-500/80 border-blue-400',
    'BC5': 'bg-purple-500/80 border-purple-400',
    'Tunnel TCM': 'bg-emerald-500/80 border-emerald-400',
    'Tunnel BEK': 'bg-amber-500/80 border-amber-400',
  };"""

new_colors = """  const groupColors: Record<string, string> = {
    'Unassigned': 'bg-bg-panel border-border',
    'BC4 A': 'bg-blue-500/80 border-blue-400',
    'BC4 B': 'bg-blue-400/80 border-blue-300',
    'BC5': 'bg-purple-500/80 border-purple-400',
    'BC4B-BC5 TRANSITION': 'bg-pink-500/80 border-pink-400',
    'FIBER A (TN BEK 5-6)': 'bg-amber-500/80 border-amber-400',
    'FIBER B (TN BEK 3-4)': 'bg-orange-500/80 border-orange-400',
    'FIBER D (TN TCM 1-6)': 'bg-emerald-500/80 border-emerald-400',
  };"""
code = code.replace(old_colors, new_colors)

# Replace Options and remove Sub Group
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

new_form = """              <option value="Unassigned">Unassigned</option>
              <option value="BC4 A">BC4 A</option>
              <option value="BC4 B">BC4 B</option>
              <option value="BC5">BC5</option>
              <option value="BC4B-BC5 TRANSITION">BC4B-BC5 TRANSITION</option>
              <option value="FIBER A (TN BEK 5-6)">FIBER A (TN BEK 5-6)</option>
              <option value="FIBER B (TN BEK 3-4)">FIBER B (TN BEK 3-4)</option>
              <option value="FIBER D (TN TCM 1-6)">FIBER D (TN TCM 1-6)</option>
            </select>
          </div>"""
code = code.replace(old_form, new_form)

# Remove Subgroup from displayed badge
old_badge = """                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold text-white border ${groupColors[mapping.main_group] || 'bg-gray-500 border-gray-400'}`}>
                        {mapping.main_group}{mapping.sub_group ? ` - ${mapping.sub_group}` : ''}
                      </span>"""
new_badge = """                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold text-white border ${groupColors[mapping.main_group] || 'bg-gray-500 border-gray-400'}`}>
                        {mapping.main_group}
                      </span>"""
code = code.replace(old_badge, new_badge)

with open('src/components/MappingGrid.tsx', 'w') as f:
    f.write(code)

