import re

with open('src/components/MappingGrid.tsx', 'r') as f:
    content = f.read()

# 1. Compute unique channels and areas
unique_computation = """
  const handleSelectAllUnassigned = () => {
    const unassigned = mappings.filter(m => m.main_group === 'Unassigned').map(m => m.id);
    setSelectedIds(new Set(unassigned));
  };
  
  const uniqueChannels = useMemo(() => Array.from(new Set(mappings.map(m => m.dts_ch))).sort((a,b) => a-b), [mappings]);
  const uniqueAreas = useMemo(() => Array.from(new Set(mappings.map(m => m.main_group))).sort(), [mappings]);

  const handleToggleChannel = (ch: number) => {
    const chIds = mappings.filter(m => m.dts_ch === ch).map(m => m.id);
    const newSet = new Set(selectedIds);
    const allSelected = chIds.length > 0 && chIds.every(id => newSet.has(id));
    if (allSelected) {
      chIds.forEach(id => newSet.delete(id));
    } else {
      chIds.forEach(id => newSet.add(id));
    }
    setSelectedIds(newSet);
  };

  const handleToggleArea = (area: string) => {
    const areaIds = mappings.filter(m => m.main_group === area).map(m => m.id);
    const newSet = new Set(selectedIds);
    const allSelected = areaIds.length > 0 && areaIds.every(id => newSet.has(id));
    if (allSelected) {
      areaIds.forEach(id => newSet.delete(id));
    } else {
      areaIds.forEach(id => newSet.add(id));
    }
    setSelectedIds(newSet);
  };
"""
content = re.sub(r'  const handleSelectAllUnassigned = \(\) => \{\n.*?  \};\n', unique_computation, content, flags=re.DOTALL)


# 2. Add the UI for quick select
quick_select_ui = """
        {/* QUICK SELECT */}
        <div className="flex flex-col space-y-2 mb-4 bg-bg-panel border border-border p-3 rounded-lg">
          <div className="flex items-center text-xs font-mono">
            <span className="text-text-secondary w-20 uppercase tracking-widest font-bold">Channels:</span>
            <div className="flex space-x-2 overflow-x-auto">
              {uniqueChannels.map(ch => {
                const chIds = mappings.filter(m => m.dts_ch === ch).map(m => m.id);
                const isAllSelected = chIds.length > 0 && chIds.every(id => selectedIds.has(id));
                return (
                  <button 
                    key={`ch-${ch}`}
                    onClick={() => handleToggleChannel(ch)}
                    className={`px-2 py-1 rounded border transition-colors ${isAllSelected ? 'bg-scada-primary/20 border-scada-primary text-scada-primary' : 'bg-bg-surface border-border text-text-secondary hover:text-text-primary'}`}
                  >
                    CH {ch}
                  </button>
                );
              })}
            </div>
          </div>
          
          <div className="flex items-center text-xs font-mono">
            <span className="text-text-secondary w-20 uppercase tracking-widest font-bold">Areas:</span>
            <div className="flex space-x-2 overflow-x-auto">
              {uniqueAreas.map(area => {
                const areaIds = mappings.filter(m => m.main_group === area).map(m => m.id);
                const isAllSelected = areaIds.length > 0 && areaIds.every(id => selectedIds.has(id));
                return (
                  <button 
                    key={`area-${area}`}
                    onClick={() => handleToggleArea(area)}
                    className={`px-2 py-1 rounded border transition-colors whitespace-nowrap ${isAllSelected ? 'bg-scada-primary/20 border-scada-primary text-scada-primary' : 'bg-bg-surface border-border text-text-secondary hover:text-text-primary'}`}
                  >
                    {area}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* LEGEND */}
"""
content = content.replace('{/* LEGEND */}', quick_select_ui)

with open('src/components/MappingGrid.tsx', 'w') as f:
    f.write(content)
