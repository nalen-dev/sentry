import re

with open('src/components/MappingGrid.tsx', 'r') as f:
    grid = f.read()

# 1. Remove the Start M and End M inputs from the form completely, and just show them as read-only if 1 segment is selected.

old_inputs = """          <div className="flex space-x-2">
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
          </div>"""

grid = grid.replace(old_inputs, "")

# 2. Revert the onUpdateBulk call to not send startM and endM
old_save = """    onUpdateBulk(
      Array.from(selectedIds), 
      selectedIds.size === 1 ? formCustomName : null,
      formMainGroup,
      formSubGroup === '' ? null : formSubGroup,
      formStartM === '' ? null : Number(formStartM),
      formEndM === '' ? null : Number(formEndM)
    )"""

new_save = """    onUpdateBulk(
      Array.from(selectedIds), 
      selectedIds.size === 1 ? formCustomName : null,
      formMainGroup,
      formSubGroup === '' ? null : formSubGroup,
      null, // Start M is native, not updated via UI
      null  // End M is native, not updated via UI
    )"""
grid = grid.replace(old_save, new_save)

# 3. Add read-only display for Start/End in the Custom Name section
old_custom = """          {selectedIds.size === 1 && (
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-text-secondary uppercase tracking-wider block">Custom Name / Alias</label>
              <input """

new_custom = """          {selectedIds.size === 1 && (
            <>
              <div className="flex space-x-2">
                <div className="space-y-1.5 flex-1">
                  <label className="text-[10px] font-bold text-text-secondary uppercase tracking-wider block">HW Start (M)</label>
                  <div className="w-full bg-bg-panel border border-border rounded-lg p-2 text-sm text-text-secondary">{formStartM !== '' ? formStartM : '-'}</div>
                </div>
                <div className="space-y-1.5 flex-1">
                  <label className="text-[10px] font-bold text-text-secondary uppercase tracking-wider block">HW End (M)</label>
                  <div className="w-full bg-bg-panel border border-border rounded-lg p-2 text-sm text-text-secondary">{formEndM !== '' ? formEndM : '-'}</div>
                </div>
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-text-secondary uppercase tracking-wider block">Custom Name / Alias</label>
                <input """
grid = grid.replace(old_custom, new_custom)

with open('src/components/MappingGrid.tsx', 'w') as f:
    f.write(grid)

