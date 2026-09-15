import { useState, useEffect } from 'react';
import { Activity, LineChart as LineChartIcon } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useNavigate } from 'react-router-dom';

interface RightPanelProps {
  totalSegments: number;
  normalSegments: number;
  warningSegments: number;
  dangerSegments: number;
  filteredAreas: any[];
}

export default function RightPanel({
  totalSegments,
  normalSegments,
  warningSegments,
  dangerSegments,
  filteredAreas
}: RightPanelProps) {
  const navigate = useNavigate();
  
  const [chartMode, setChartMode] = useState<'area' | 'history'>('area');
  const [historyData, setHistoryData] = useState<any[]>([]);
  const [histGroups, setHistGroups] = useState<string[]>([]);
  
  // Fetch group history (like Chart Menu)
  useEffect(() => {
    let isMounted = true;
    import('@tauri-apps/api/core').then(({ invoke }) => {
      const fetchHistory = async () => {
        if (chartMode !== 'history') return;
        
        try {
          const data: any[] = await invoke('get_groups_history', { minutes: 30 });
          if (!isMounted) return;
          
          if (data.length === 0) {
            setHistoryData([]);
            return;
          }
          
          const groupsSet = new Set<string>();
          const flatData = data.map(pt => {
            const row: any = { time: pt.time };
            for (const [g, val] of Object.entries(pt.groups)) {
              row[g] = val;
              groupsSet.add(g);
            }
            return row;
          });
          
          setHistGroups(Array.from(groupsSet).sort());
          setHistoryData(flatData);
        } catch (err) {
          console.error("Failed to fetch group history for RightPanel", err);
        }
      };
      
      fetchHistory();
      const timer = setInterval(fetchHistory, 10000);
      return () => { isMounted = false; clearInterval(timer); };
    });
  }, [chartMode]);

  // Prepare Area Chart Data
  const areaChartData = filteredAreas.map(a => ({
    name: a.name,
    distance: a.distance,
    temp: a.temp_avg || 0
  }));

  return (
    <>
      {/* SYSTEM STATISTICS */}
      <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl p-4 shadow-lg pointer-events-auto shrink-0 flex flex-col mt-4">
        <div className="text-sm font-bold text-text-primary uppercase tracking-widest flex items-center border-b border-border pb-2 mb-3">
          <Activity size={16} className="mr-2 text-scada-primary" /> SEGMENT STATS
        </div>
        <div className="grid grid-cols-4 gap-2 text-center">
          <div className="flex flex-col bg-bg-surface p-2 rounded border border-border">
            <span className="text-lg font-mono font-bold text-text-primary">{totalSegments}</span>
            <span className="text-[9px] text-text-secondary uppercase font-bold tracking-widest mt-1">Total</span>
          </div>
          <div className="flex flex-col bg-bg-surface p-2 rounded border border-border">
            <span className="text-lg font-mono font-bold text-scada-success">{normalSegments}</span>
            <span className="text-[9px] text-text-secondary uppercase font-bold tracking-widest mt-1">Normal</span>
          </div>
          <div className="flex flex-col bg-bg-surface p-2 rounded border border-border">
            <span className="text-lg font-mono font-bold text-yellow-500">{warningSegments}</span>
            <span className="text-[9px] text-text-secondary uppercase font-bold tracking-widest mt-1">Warn</span>
          </div>
          <div className="flex flex-col bg-bg-alarm/50 p-2 rounded border border-red-500/30">
            <span className="text-lg font-mono font-bold text-red-500">{dangerSegments}</span>
            <span className="text-[9px] text-red-400 uppercase font-bold tracking-widest mt-1">Danger</span>
          </div>
        </div>
      </div>

      {/* TEMPERATURE CHART */}
      <div 
        onClick={() => navigate('/chart')}
        className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl p-4 shadow-lg pointer-events-auto flex-1 flex flex-col min-h-0 mt-4 transition-colors group"
      >
        <div className="text-sm font-bold text-text-primary uppercase tracking-widest flex items-center justify-between border-b border-border pb-2 mb-3 shrink-0">
          <div className="flex items-center">
            <LineChartIcon size={16} className="mr-2 text-scada-primary group-hover:scale-110 transition-transform" /> TEMPERATURE TREND
          </div>
          <div className="flex bg-bg-base p-1 rounded-md cursor-pointer" onClick={(e) => { e.stopPropagation(); }}>
            <button onClick={() => setChartMode('area')} className={`text-[9px] px-2 py-1 rounded transition-colors ${chartMode === 'area' ? 'bg-bg-surface text-scada-primary' : 'text-text-secondary hover:text-text-primary'}`}>PER AREA</button>
            <button onClick={() => setChartMode('history')} className={`text-[9px] px-2 py-1 rounded transition-colors ${chartMode === 'history' ? 'bg-bg-surface text-scada-primary' : 'text-text-secondary hover:text-text-primary'}`}>GROUP HISTORY (30M)</button>
          </div>
        </div>
        <div className="flex-1 w-full min-h-0 cursor-pointer">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartMode === 'area' ? areaChartData : historyData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" opacity={0.3} />
              <XAxis dataKey={chartMode === 'area' ? "name" : "time"} stroke="#9ca3af" fontSize={10} tickMargin={5} />
              <YAxis stroke="#9ca3af" fontSize={10} />
              <Tooltip 
                contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', fontSize: '12px' }}
                itemStyle={{ fontWeight: 'bold' }}
                labelStyle={{ color: 'var(--text-secondary)' }}
              />
              {chartMode === 'area' ? (
                <Line type="monotone" dataKey="temp" name="Temperature" stroke="var(--scada-primary)" strokeWidth={2} dot={{ r: 3, fill: 'var(--scada-primary)', strokeWidth: 0 }} activeDot={{ r: 5, strokeWidth: 0 }} />
              ) : (
                histGroups.map((name, i) => (
                  <Line key={name} type="monotone" dataKey={name} name={name} stroke={['#06b6d4', '#eab308', '#ef4444', '#10b981', '#a855f7', '#f97316'][i % 6]} strokeWidth={2} dot={false} activeDot={{ r: 4, strokeWidth: 0 }} />
                ))
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </>
  );
}
