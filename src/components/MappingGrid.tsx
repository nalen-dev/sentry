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
  onUpdateBulk: (ids: number[], customName: string | null, mainGroup: string, subGroup: string | null) => Promise<void>;
}

export default function MappingGrid({ mappings, onUpdateBulk }: MappingGridProps) {
  const { showToast } = useToast();
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [lastClickedId, setLastClickedId] = useState<number | null>(null);

  // Form states
  const [formMainGroup, setFormMainGroup] = useState('Unassigned');
  const [formSubGroup, setFormSubGroup] = useState('');
  const [formCustomName, setFormCustomName] = useState('');

  // Group Colors mapping
  const groupColors: Record<string, string> = {
    'Unassigned': 'bg-bg-panel border-border',
    'BC4': 'bg-blue-500/80 border-blue-400',
    'BC5': 'bg-purple-500/80 border-purple-400',
    'Tunnel TCM': 'bg-emerald-500/80 border-emerald-400',
    'Tunnel BEK': 'bg-amber-500/80 border-amber-400',
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
        setFormSubGroup(selected.sub_group || '');
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

  const handleSave = async () => {
    if (selectedIds.size === 0) return;
    
    try {
      await onUpdateBulk(
        Array.from(selectedIds), 
        selectedIds.size === 1 ? (formCustomName || null) : null,
        formMainGroup, 
        formSubGroup || null
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
          </div>

          {selectedIds.size === 1 && (
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
