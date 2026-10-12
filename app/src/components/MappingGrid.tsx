import React, { useState, useMemo } from 'react';
import { Save, CheckSquare, Info } from 'lucide-react';
import { useToast } from '../contexts/ToastContext';

export interface SegmentMapping {
  id: number;
  dts_ch: number;
  dts_code: number;
  original_name: string;
  custom_name: string | null;
  main_group: string;
  sub_group: string | null;
  start_m?: number | null;
  end_m?: number | null;
}

interface MappingGridProps {
  mappings: SegmentMapping[];
  onUpdateBulk: (ids: number[], customName: string | null, mainGroup: string, subGroup: string | null, startM: number | null, endM: number | null) => Promise<void>;
}

export default function MappingGrid({ mappings, onUpdateBulk }: MappingGridProps) {
  const { showToast } = useToast();
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [lastClickedId, setLastClickedId] = useState<number | null>(null);

  // Form states
  const [formMainGroup, setFormMainGroup] = useState('Unassigned');
  const [formSubGroup, setFormSubGroup] = useState('');
  const [formStartM, setFormStartM] = useState<number | ''>('');
  const [formEndM, setFormEndM] = useState<number | ''>('');
  const [formCustomName, setFormCustomName] = useState('');

  // Sync form when selection changes
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
  }, [selectedIds, mappings]);

  // Group Colors mapping
  const groupColors: Record<string, string> = {
    'Unassigned': 'bg-bg-panel border-border',
    'BC4 A': 'bg-blue-500/80 border-blue-400',
    'BC4 B': 'bg-blue-400/80 border-blue-300',
    'BC5': 'bg-purple-500/80 border-purple-400',
    'BC45-MOTOR': 'bg-pink-500/80 border-pink-400',
    'BEK56': 'bg-amber-500/80 border-amber-400',
    'BEK34': 'bg-orange-500/80 border-orange-400',
    'TCM16': 'bg-emerald-500/80 border-emerald-400',
  };

  const handleBoxClick = (e: React.MouseEvent, mapId: number, index: number) => {
    const newSet = new Set(selectedIds);
    
    if (e.shiftKey && lastClickedId !== null) {
      // Find index of last clicked
      const lastIndex = mappings.findIndex(m => m.id === lastClickedId);
      if (lastIndex !== -1) {
        const start = Math.min(lastIndex, index);
        const end = Math.max(lastIndex, index);
        for (let i = start; i <= end; i++) {
          newSet.add(mappings[i].id);
        }
      }
    } else if (e.ctrlKey || e.metaKey) {
      if (newSet.has(mapId)) newSet.delete(mapId);
      else newSet.add(mapId);
    } else {
      if (newSet.has(mapId) && newSet.size === 1) {
        newSet.clear();
      } else {
        newSet.clear();
        newSet.add(mapId);
      }
    }
    
    setSelectedIds(newSet);
    setLastClickedId(mapId);

    // Auto-fill form if single select
    if (newSet.size === 1) {
      const selected = mappings.find(m => m.id === Array.from(newSet)[0]);
      if (selected) {
        setFormMainGroup(selected.main_group);
        setFormStartM(selected.start_m ?? '');
        setFormEndM(selected.end_m ?? '');
        setFormCustomName(selected.custom_name || '');
      }
    } else {
      setFormCustomName('');
    }
  };


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

  const handleSave = async () => {
    if (selectedIds.size === 0) return;
    
    try {
      await onUpdateBulk(
        Array.from(selectedIds), 
        selectedIds.size === 1 ? (formCustomName || null) : null,
        formMainGroup, 
        formSubGroup === '' ? null : formSubGroup,
        formStartM === '' ? null : Number(formStartM),
        formEndM === '' ? null : Number(formEndM)
      );
      showToast(`Successfully updated ${selectedIds.size} segments!`, 'success');
    } catch (e) {
      showToast(`Failed to update segments`, 'error');
    }
  };

  const selectedSegments = useMemo(() => {
    return mappings.filter(m => selectedIds.has(m.id));
  }, [mappings, selectedIds]);

  return (
    <div className="flex space-x-6 h-[600px]">
      
      {/* LEFT: GITHUB STYLE GRID */}
      <div className="flex-1 bg-bg-surface border border-border rounded-xl p-6 flex flex-col min-h-0">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h4 className="text-sm font-bold text-text-primary uppercase tracking-widest">Visual Segment Map</h4>
            <p className="text-xs text-text-secondary mt-1">Shift-click to select range. Ctrl-click to add.</p>
          </div>
          <button 
            onClick={handleSelectAllUnassigned}
            className="px-3 py-1.5 bg-bg-panel border border-border rounded text-xs font-bold text-text-secondary hover:text-text-primary transition-colors flex items-center"
          >
            <CheckSquare size={14} className="mr-2" /> Select All Unassigned
          </button>
        </div>

        
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

        <div className="flex space-x-3 mb-4 flex-wrap gap-y-2">
          {Object.entries(groupColors).map(([name, colorClass]) => (
            <div key={name} className="flex items-center text-xs text-text-secondary">
              <div className={`w-3 h-3 rounded-sm border ${colorClass} mr-1.5 opacity-80`} />
              {name}
            </div>
          ))}
        </div>

        {/* GRID CONTAINER */}
        <div className="flex-1 overflow-y-auto custom-scrollbar pr-2">
          <div className="flex flex-wrap gap-1.5">
            {mappings.map((map, idx) => {
              const isSelected = selectedIds.has(map.id);
              const colorClass = groupColors[map.main_group] || groupColors['Unassigned'];
              
              return (
                <div
                  key={map.id}
                  onClick={(e) => handleBoxClick(e, map.id, idx)}
                  title={`CH${map.dts_ch}-C${map.dts_code} | ${map.original_name}\nGroup: ${map.main_group}`}
                  className={`
                    w-4 h-4 rounded-sm cursor-pointer transition-all border
                    ${isSelected ? 'ring-2 ring-white ring-offset-1 ring-offset-bg-surface scale-125 z-10' : 'hover:ring-1 hover:ring-text-secondary hover:scale-110'}
                    ${colorClass}
                  `}
                />
              );
            })}
          </div>
        </div>
      </div>

      {/* RIGHT: EDITOR PANEL */}
      <div className="w-80 bg-bg-surface border border-border rounded-xl p-6 flex flex-col shrink-0">
        <div className="mb-6">
          <h4 className="text-sm font-bold text-text-primary uppercase tracking-widest">Selection Editor</h4>
          <p className="text-xs font-mono text-scada-primary mt-1">{selectedIds.size} Segments Selected</p>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar mb-6 space-y-4">
          
          <div className="space-y-1.5">
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

          

          {selectedIds.size === 1 && (
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
                <input 
                type="text" 
                value={formCustomName}
                onChange={e => setFormCustomName(e.target.value)}
                placeholder="Alias (e.g. Area 1)"
                className="w-full bg-bg-panel border border-border rounded-lg p-2 text-sm text-text-primary focus:outline-none focus:border-scada-primary"
              />
            </div>
            </>
          )}

          {selectedIds.size > 1 && (
            <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg flex items-start">
              <Info size={14} className="text-blue-400 mr-2 mt-0.5 shrink-0" />
              <p className="text-xs text-blue-400">Custom names can only be edited when selecting exactly 1 segment.</p>
            </div>
          )}

          <div className="pt-4 border-t border-border">
            <h5 className="text-xs font-bold text-text-secondary mb-2 uppercase tracking-widest">Selected List:</h5>
            <div className="space-y-1 max-h-48 overflow-y-auto custom-scrollbar pr-2">
              {selectedSegments.length === 0 && (
                <span className="text-xs text-text-secondary italic">No segments selected</span>
              )}
              {selectedSegments.map(s => (
                <div key={s.id} className="text-xs font-mono bg-bg-panel border border-border p-1.5 rounded truncate text-text-primary">
                  <span className="text-text-secondary mr-2">CH{s.dts_ch}-C{s.dts_code}</span> 
                  {s.custom_name || s.original_name}
                </div>
              ))}
            </div>
          </div>
        </div>

        <button 
          onClick={handleSave}
          disabled={selectedIds.size === 0}
          className="w-full py-3 bg-scada-primary/20 hover:bg-scada-primary text-scada-primary hover:text-white transition-colors border border-scada-primary/50 rounded-lg font-bold text-sm flex items-center justify-center disabled:opacity-30 disabled:hover:bg-scada-primary/20 disabled:hover:text-scada-primary"
        >
          <Save size={16} className="mr-2" /> 
          APPLY TO {selectedIds.size} SEGMENTS
        </button>

      </div>
    </div>
  );
}
