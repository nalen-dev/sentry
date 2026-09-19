import re

with open('src/features/dashboard/DataModal.tsx', 'r') as f:
    code = f.read()

target = """      </div>

      <div className="flex-1 bg-bg-panel border border-border rounded-xl overflow-hidden flex flex-col shadow-2xl relative">"""

toolbar = """      </div>

      {/* TOOLBAR */}
      <div className="flex flex-col sm:flex-row gap-3 mb-4 p-4 border border-border bg-bg-panel rounded-xl shadow-md">
        <div className="relative flex-1">
          <input 
            type="text" 
            placeholder="Search segments..." 
            value={searchQuery}
            onChange={e => { setSearchQuery(e.target.value); setTablePage(1); }}
            className="w-full bg-bg-surface border border-border rounded-lg pl-10 pr-4 py-2 text-sm text-text-primary outline-none focus:border-scada-primary transition-colors"
          />
          <Search size={16} className="absolute left-3 top-2.5 text-text-secondary" />
        </div>
        <div className="flex gap-2 overflow-x-auto">
          <select
            value={filterGroup}
            onChange={e => { setFilterGroup(e.target.value); setTablePage(1); }}
            className="bg-bg-surface border border-border rounded-lg px-3 py-2 text-sm text-text-secondary font-bold outline-none focus:border-scada-primary whitespace-nowrap"
          >
            <option value="All">ALL GROUPS</option>
            {Array.from(new Set(areas.map(a => a.mainGroup))).filter(g => g !== 'Unassigned').map(g => (
              <option key={g} value={g}>{g}</option>
            ))}
          </select>
          {viewMode === 'table' && (
            <select
              value={sortBy}
              onChange={e => { setSortBy(e.target.value); setTablePage(1); }}
              className="bg-bg-surface border border-border rounded-lg px-3 py-2 text-sm text-text-secondary font-bold outline-none focus:border-scada-primary whitespace-nowrap"
            >
              <option value="default">DEFAULT SORT</option>
              <option value="temp_desc">HIGHEST TEMP</option>
              <option value="temp_asc">LOWEST TEMP</option>
              <option value="dist_desc">FURTHEST DISTANCE</option>
              <option value="dist_asc">CLOSEST DISTANCE</option>
            </select>
          )}
        </div>
      </div>

      <div className="flex-1 bg-bg-panel border border-border rounded-xl overflow-hidden flex flex-col shadow-2xl relative">"""

code = code.replace(target, toolbar)

with open('src/features/dashboard/DataModal.tsx', 'w') as f:
    f.write(code)

