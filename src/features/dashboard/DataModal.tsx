import { useState, useMemo } from 'react';
import { List, X, Grid, ChevronDown, ChevronUp, MapPin, ChevronLeft, ChevronRight } from 'lucide-react';
import { SegmentData } from '../../components/SegmentDetailModal';

interface DataModalProps {
  onClose: () => void;
  areas: (SegmentData & { mainGroup: string; subGroup: string | null })[];
  setSelectedSegment: (segment: SegmentData) => void;
}

export default function DataModal({ onClose, areas, setSelectedSegment }: DataModalProps) {
  const [viewMode, setViewMode] = useState<'grouped' | 'table'>('grouped');
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({});
  const [groupPages, setGroupPages] = useState<Record<string, number>>({});
  const [tablePage, setTablePage] = useState(1);

  const toggleGroup = (groupName: string) => {
    setExpandedGroups(prev => ({
      ...prev,
      [groupName]: !prev[groupName]
    }));
  };

  const handleGroupPageChange = (groupName: string, delta: number) => {
    setGroupPages(prev => ({
      ...prev,
      [groupName]: (prev[groupName] || 1) + delta
    }));
  };




  // Group data
  const groupedData = useMemo(() => {
    const groups: Record<string, typeof areas> = {};
    areas.forEach(area => {
      const g = area.mainGroup === 'Unassigned' ? 'Not Set (Unassigned)' : area.mainGroup;
      if (!groups[g]) groups[g] = [];
      groups[g].push(area);
    });

    // Calculate stats for each group
    const result = Object.entries(groups).map(([groupName, groupAreas]) => {
      const sorted = [...groupAreas].sort((a, b) => b.temp - a.temp);
      const avg = sorted.reduce((sum, item) => sum + item.temp, 0) / (sorted.length || 1);
      
      return {
        groupName,
        averageTemp: avg.toFixed(1),
        top5: sorted.slice(0, 5),
        others: sorted.slice(5),
        totalItems: sorted.length
      };
    });

    return result.sort((a, b) => a.groupName.localeCompare(b.groupName));
  }, [areas]);


  return (
    <div className="absolute inset-0 z-50 flex flex-col bg-bg-base/95 backdrop-blur-md p-8 animate-in fade-in zoom-in-95 duration-200">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center">
          <List className="text-scada-primary mr-3" size={28} />
          <div>
            <h2 className="text-text-primary font-bold tracking-widest text-2xl uppercase">COMPLETE SEGMENT DATA</h2>
            <p className="text-text-secondary font-mono text-sm">GROUPED TEMPERATURE MONITORING</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex bg-bg-panel/50 p-1 rounded-lg border border-border">
            <button
              onClick={() => setViewMode('grouped')}
              className={`p-2 rounded-md flex items-center transition-all ${viewMode === 'grouped' ? 'bg-bg-surface text-text-primary shadow-sm border border-border' : 'text-text-secondary hover:text-text-primary border border-transparent'}`}
              title="Grouped View"
            >
              <Grid size={18} />
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`p-2 rounded-md flex items-center transition-all ${viewMode === 'table' ? 'bg-bg-surface text-text-primary shadow-sm border border-border' : 'text-text-secondary hover:text-text-primary border border-transparent'}`}
              title="Flat Table"
            >
              <List size={18} />
            </button>
          </div>

          <button 
            onClick={onClose}
            className="p-3 bg-red-500/10 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors border border-red-500/30"
          >
            <X size={24} />
          </button>
        </div>
      </div>

      <div className="flex-1 bg-bg-panel border border-border rounded-xl overflow-hidden flex flex-col shadow-2xl relative">
        
        {viewMode === 'grouped' && (
          <div className="overflow-y-auto flex-1 custom-scrollbar p-6 space-y-6">
            {groupedData.map(group => (
              <div key={group.groupName} className="bg-bg-surface border border-border rounded-xl p-5 shadow-lg">
                
                {/* GROUP HEADER */}
                <div className="flex justify-between items-center mb-4 pb-4 border-b border-border">
                  <div>
                    <h3 className="text-lg font-bold text-text-primary tracking-wider uppercase flex items-center">
                      <MapPin size={18} className="mr-2 text-scada-primary" />
                      {group.groupName}
                    </h3>
                    <p className="text-xs font-mono text-text-secondary mt-1">Total Segments: {group.totalItems}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-bold text-text-secondary uppercase tracking-widest block mb-1">Group Average</span>
                    <span className="text-2xl font-mono font-bold text-scada-primary">{group.averageTemp}°C</span>
                  </div>
                </div>

                {/* TOP 5 */}
                <h4 className="text-xs font-bold text-text-secondary uppercase mb-3 text-red-400">Top 5 Highest Temperature</h4>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3 mb-4">
                  {group.top5.map(area => (
                    <div 
                      key={area.id} 
                      onClick={() => { setSelectedSegment(area); onClose(); }}
                      className={`p-3 rounded-lg flex flex-col cursor-pointer transition-all hover:scale-105 shadow-md border ${area.isAlarm ? 'bg-bg-alarm border-red-500/50' : 'bg-bg-base border-border hover:bg-bg-surface'}`}
                    >
                      <span className={`font-bold text-sm truncate ${area.isAlarm ? 'text-red-400' : 'text-text-primary'}`}>{area.name}</span>
                      <div className="flex justify-between items-end mt-2">
                        <span className="text-xs text-text-secondary truncate pr-2">{area.distance}</span>
                        <span className={`font-mono font-bold ${area.isAlarm ? 'text-red-400' : 'text-scada-success'}`}>{area.temp}°C</span>
                      </div>
                    </div>
                  ))}
                </div>

                {/* OTHERS (EXPANDABLE) */}
                {group.others.length > 0 && (
                  <div>
                    <button 
                      onClick={() => toggleGroup(group.groupName)}
                      className="w-full py-2 bg-bg-base hover:bg-bg-panel border border-border rounded-lg text-xs font-bold text-text-secondary hover:text-scada-primary transition-colors flex items-center justify-center uppercase tracking-widest"
                    >
                      {expandedGroups[group.groupName] ? (
                        <><ChevronUp size={14} className="mr-2" /> Hide Other {group.others.length} Segments</>
                      ) : (
                        <><ChevronDown size={14} className="mr-2" /> Show Other {group.others.length} Segments</>
                      )}
                    </button>

                    {expandedGroups[group.groupName] && (
                      <div className="mt-3 animate-in fade-in slide-in-from-top-2">
                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2 mb-3">
                        {group.others.slice(((groupPages[group.groupName] || 1) - 1) * 10, (groupPages[group.groupName] || 1) * 10).map(area => (
                          <div 
                            key={area.id} 
                            onClick={() => { setSelectedSegment(area); onClose(); }}
                            className={`p-2 rounded flex flex-col cursor-pointer transition-all hover:scale-105 border ${area.isAlarm ? 'bg-bg-alarm border-red-500/50' : 'bg-bg-base border-border hover:bg-bg-surface'}`}
                          >
                            <span className="font-bold text-xs truncate text-text-primary">{area.name}</span>
                            <div className="flex justify-between items-end mt-1">
                              <span className="text-[10px] text-text-secondary truncate">{area.distance}</span>
                              <span className="font-mono text-xs font-bold text-scada-success">{area.temp_avg ?? area.temp}°C</span>
                            </div>
                          </div>
                        ))}
                        </div>
                        {group.others.length > 10 && (
                          <div className="flex justify-center items-center space-x-4 mt-2">
                            <button onClick={() => handleGroupPageChange(group.groupName, -1)} disabled={(groupPages[group.groupName] || 1) === 1} className="p-1 rounded bg-bg-panel disabled:opacity-30"><ChevronLeft size={16}/></button>
                            <span className="text-xs text-text-secondary">Page {groupPages[group.groupName] || 1} of {Math.ceil(group.others.length / 10)}</span>
                            <button onClick={() => handleGroupPageChange(group.groupName, 1)} disabled={(groupPages[group.groupName] || 1) === Math.ceil(group.others.length / 10)} className="p-1 rounded bg-bg-panel disabled:opacity-30"><ChevronRight size={16}/></button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* FLAT TABLE VIEW */}
        {viewMode === 'table' && (
          <div className="flex flex-col flex-1 overflow-hidden">
          <div className="overflow-auto flex-1 custom-scrollbar mb-2">
            <table className="w-full text-left border-collapse">
              <thead className="bg-bg-surface sticky top-0 z-10 shadow-md">
                <tr>
                  <th className="py-4 px-6 text-text-secondary font-bold uppercase text-xs tracking-wider border-b border-border">Group</th>
                  <th className="py-4 px-6 text-text-secondary font-bold uppercase text-xs tracking-wider border-b border-border">Area Name</th>
                  <th className="py-4 px-6 text-text-secondary font-bold uppercase text-xs tracking-wider border-b border-border">Distance</th>
                  <th className="py-4 px-6 text-text-secondary font-bold uppercase text-xs tracking-wider border-b border-border">Avg Temp</th>
                  <th className="py-4 px-6 text-text-secondary font-bold uppercase text-xs tracking-wider border-b border-border">Min Temp</th>
                  <th className="py-4 px-6 text-text-secondary font-bold uppercase text-xs tracking-wider border-b border-border">Max Temp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {areas.slice((tablePage - 1) * 10, tablePage * 10).map((area) => (
                  <tr key={area.id} onClick={() => { setSelectedSegment(area); onClose(); }} className="cursor-pointer hover:bg-white/[0.02] transition-colors">
                    <td className="py-3 px-6 font-bold text-text-secondary text-sm">{area.mainGroup === 'Unassigned' ? 'Not Set' : area.mainGroup}</td>
                    <td className="py-3 px-6 font-bold text-text-primary">{area.name}</td>
                    <td className="py-3 px-6 font-mono text-text-secondary">{area.distance}</td>
                    <td className={`py-3 px-6 font-mono font-bold ${area.isAlarm ? 'text-red-400' : 'text-scada-success'}`}>
                      {area.temp_avg ?? area.temp}°C
                    </td>
                    <td className="py-3 px-6 font-mono text-blue-400">
                      {area.temp_min ?? '-'}°C
                    </td>
                    <td className="py-3 px-6 font-mono text-red-400">
                      {area.temp_max ?? '-'}°C
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {/* Table Pagination */}
          {areas.length > 10 && (
            <div className="flex justify-between items-center px-6 py-3 bg-bg-surface border-t border-border">
              <span className="text-xs text-text-secondary">Showing {(tablePage - 1) * 10 + 1} to {Math.min(tablePage * 10, areas.length)} of {areas.length} entries</span>
              <div className="flex space-x-2">
                <button onClick={() => setTablePage(p => p - 1)} disabled={tablePage === 1} className="px-3 py-1 bg-bg-panel rounded border border-border text-xs disabled:opacity-50 hover:bg-bg-surface transition-colors">Previous</button>
                <button onClick={() => setTablePage(p => p + 1)} disabled={tablePage === Math.ceil(areas.length / 10)} className="px-3 py-1 bg-bg-panel rounded border border-border text-xs disabled:opacity-50 hover:bg-bg-surface transition-colors">Next</button>
              </div>
            </div>
          )}
          </div>
        )}

      </div>
    </div>
  );
}
