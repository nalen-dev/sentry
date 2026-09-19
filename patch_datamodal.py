import re

with open('src/features/dashboard/DataModal.tsx', 'r') as f:
    code = f.read()

# 1. Add Search import
code = code.replace("from 'lucide-react';", ", Search } from 'lucide-react';")

# 2. Add states
state_insertion = """  const [viewMode, setViewMode] = useState<'grouped' | 'table'>('grouped');
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({});
  const [groupPages, setGroupPages] = useState<Record<string, number>>({});
  const [tablePage, setTablePage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterGroup, setFilterGroup] = useState<string>('All');
  const [sortBy, setSortBy] = useState<string>('default');"""

code = code.replace("  const [viewMode, setViewMode] = useState<'grouped' | 'table'>('grouped');\n  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({});\n  const [groupPages, setGroupPages] = useState<Record<string, number>>({});\n  const [tablePage, setTablePage] = useState(1);", state_insertion)

# 3. Add filteredAreas logic
filtered_logic = """  const filteredAreas = useMemo(() => {
    let result = [...areas];
    if (filterGroup !== 'All') {
      result = result.filter(a => a.mainGroup === filterGroup);
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(a => a.name.toLowerCase().includes(q));
    }
    if (viewMode === 'table') {
      if (sortBy === 'temp_desc') {
        result.sort((a, b) => (b.temp_max ?? b.temp) - (a.temp_max ?? a.temp));
      } else if (sortBy === 'temp_asc') {
        result.sort((a, b) => (a.temp_max ?? a.temp) - (b.temp_max ?? b.temp));
      } else if (sortBy === 'dist_desc') {
        result.sort((a, b) => (parseFloat(b.distance) || 0) - (parseFloat(a.distance) || 0));
      } else if (sortBy === 'dist_asc') {
        result.sort((a, b) => (parseFloat(a.distance) || 0) - (parseFloat(b.distance) || 0));
      }
    }
    return result;
  }, [areas, filterGroup, searchQuery, viewMode, sortBy]);

  // Group data
  const groupedData = useMemo(() => {
    const groups: Record<string, typeof areas> = {};
    filteredAreas.forEach(area => {"""

code = code.replace("""  // Group data
  const groupedData = useMemo(() => {
    const groups: Record<string, typeof areas> = {};
    areas.forEach(area => {""", filtered_logic)

# Replace areas dependency with filteredAreas in groupedData
code = code.replace("  }, [areas]);", "  }, [filteredAreas]);")

# Replace areas with filteredAreas in table view
code = code.replace("{areas.slice((tablePage - 1) * 10, tablePage * 10).map((area) => (", "{filteredAreas.slice((tablePage - 1) * 10, tablePage * 10).map((area) => (")
code = code.replace("{areas.length > 10 && (", "{filteredAreas.length > 10 && (")
code = code.replace("of {areas.length} entries", "of {filteredAreas.length} entries")
code = code.replace("Math.ceil(areas.length / 10)", "Math.ceil(filteredAreas.length / 10)")
code = code.replace("Total {areas.length} mapped segments", "Total {filteredAreas.length} mapped segments")


# 4. Insert Toolbar
toolbar = """        </div>

        {/* TOOLBAR */}
        <div className="flex flex-col sm:flex-row gap-3 p-4 border-b border-border bg-bg-base">
          <div className="relative flex-1">
            <input 
              type="text" 
              placeholder="Search segments..." 
              value={searchQuery}
              onChange={e => { setSearchQuery(e.target.value); setTablePage(1); }}
              className="w-full bg-bg-surface border border-border rounded-lg pl-10 pr-4 py-2 text-sm text-text-primary outline-none focus:border-scada-primary"
            />
            <Search size={16} className="absolute left-3 top-2.5 text-text-secondary" />
          </div>
          <div className="flex gap-2 overflow-x-auto">
            <select
              value={filterGroup}
              onChange={e => { setFilterGroup(e.target.value); setTablePage(1); }}
              className="bg-bg-surface border border-border rounded-lg px-3 py-2 text-sm text-text-secondary outline-none focus:border-scada-primary whitespace-nowrap"
            >
              <option value="All">All Groups</option>
              {Array.from(new Set(areas.map(a => a.mainGroup))).filter(g => g !== 'Unassigned').map(g => (
                <option key={g} value={g}>{g}</option>
              ))}
            </select>
            {viewMode === 'table' && (
              <select
                value={sortBy}
                onChange={e => { setSortBy(e.target.value); setTablePage(1); }}
                className="bg-bg-surface border border-border rounded-lg px-3 py-2 text-sm text-text-secondary outline-none focus:border-scada-primary whitespace-nowrap"
              >
                <option value="default">Default Sort</option>
                <option value="temp_desc">Highest Temp</option>
                <option value="temp_asc">Lowest Temp</option>
                <option value="dist_desc">Furthest Distance</option>
                <option value="dist_asc">Closest Distance</option>
              </select>
            )}
          </div>
        </div>

        {/* CONTENT */}"""

code = code.replace("""        </div>

        {/* GROUPED VIEW */""", toolbar + "\n\n        {/* GROUPED VIEW */")


with open('src/features/dashboard/DataModal.tsx', 'w') as f:
    f.write(code)

