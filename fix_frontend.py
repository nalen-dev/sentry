import re

# 1. Fix ChartPage.tsx
with open('src/pages/ChartPage.tsx', 'r') as f:
    cp = f.read()
cp = cp.replace(
    "const minutes = selectedTimeRange === '30m' ? 30 : selectedTimeRange === '1h' ? 60 : selectedTimeRange === '6h' ? 360 : 30;\n          const data: any[] = await invoke('get_groups_history', { minutes });",
    "const limit = selectedTimeRange === '30m' ? 180 : selectedTimeRange === '1h' ? 360 : selectedTimeRange === '6h' ? 2160 : 180;\n          const data: any[] = await invoke('get_groups_history', { limit });"
)
with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(cp)


# 2. Fix SegmentDetailModal.tsx
with open('src/components/SegmentDetailModal.tsx', 'r') as f:
    sm = f.read()
sm = sm.replace("minutes: 30", "limit: 180")
with open('src/components/SegmentDetailModal.tsx', 'w') as f:
    f.write(sm)


# 3. Rewrite RightPanel.tsx to match ChartPage.tsx exactly (no toggle)
right_panel_content = """import { useState, useEffect } from 'react';
import { Activity, LineChart as LineChartIcon } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine } from 'recharts';
import { useNavigate } from 'react-router-dom';

const COLORS = ['#06b6d4', '#eab308', '#ef4444', '#10b981', '#a855f7', '#f97316', '#3b82f6', '#ec4899', '#14b8a6', '#f43f5e'];

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
}: RightPanelProps) {
  const navigate = useNavigate();
  const [historyData, setHistoryData] = useState<any[]>([]);
  const [histGroups, setHistGroups] = useState<string[]>([]);
  
  // Fetch group history (like Chart Menu)
  useEffect(() => {
    let isMounted = true;
    import('@tauri-apps/api/core').then(({ invoke }) => {
      const fetchHistory = async () => {
        try {
          const data: any[] = await invoke('get_groups_history', { limit: 180 });
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
  }, []);

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
            <LineChartIcon size={16} className="mr-2 text-scada-primary group-hover:scale-110 transition-transform" /> TEMPERATURE TREND (30M)
          </div>
        </div>
        <div className="flex-1 w-full min-h-0 cursor-pointer">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={historyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" opacity={0.3} vertical={false} />
                <XAxis dataKey="time" stroke="#9ca3af" fontSize={10} tickMargin={5} />
                <YAxis stroke="#9ca3af" fontSize={10} domain={['dataMin - 5', 'dataMax + 5']} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', fontSize: '10px' }}
                  itemStyle={{ fontWeight: 'bold' }}
                  labelStyle={{ color: 'var(--text-secondary)' }}
                />
                <Legend verticalAlign="top" height={24} iconType="circle" wrapperStyle={{ fontSize: '10px' }} />
                
                <ReferenceLine y={60} stroke="#ef4444" strokeDasharray="5 5" label={{ position: 'insideTopLeft', value: 'WARN', fill: '#ef4444', fontSize: 9, fontWeight: 'bold' }} />
                
                {histGroups.map((name, i) => (
                  <Line key={name} type="monotone" dataKey={name} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={false} activeDot={{ r: 4, strokeWidth: 0 }} />
                ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </>
  );
}
"""

with open('src/features/dashboard/RightPanel.tsx', 'w') as f:
    f.write(right_panel_content)

