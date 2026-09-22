import { useState, useEffect } from 'react';
import { LineChart as LineChartIcon } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine } from 'recharts';
import { useNavigate } from 'react-router-dom';

const COLORS = ['#06b6d4', '#eab308', '#ef4444', '#10b981', '#a855f7', '#f97316', '#3b82f6', '#ec4899', '#14b8a6', '#f43f5e'];

interface RightPanelProps {}

export default function RightPanel({}: RightPanelProps = {}) {
  const navigate = useNavigate();
  const [historyData, setHistoryData] = useState<any[]>([]);
  const [histGroups, setHistGroups] = useState<string[]>([]);
  
  // Fetch group history (like Chart Menu)
  useEffect(() => {
    let isMounted = true;
    import('@tauri-apps/api/core').then(({ invoke }) => {
      const fetchHistory = async () => {
        try {
          const [data, mappingsData] = await Promise.all([
             invoke<any[]>('get_groups_history', { 
               startDt: (new Date(Date.now() - 30 * 60000)).toLocaleString('sv').replace('T', ' ').substring(0, 19), 
               endDt: (new Date()).toLocaleString('sv').replace('T', ' ').substring(0, 19) 
             }),
             invoke<any[]>('get_segment_mappings')
          ]);
          if (!isMounted) return;
          
          if (data.length === 0) {
            setHistoryData([]);
            return;
          }
          
          const groupsSet = new Set<string>();
          mappingsData.forEach(m => {
            if (m.main_group && m.main_group !== 'Unassigned') {
              groupsSet.add(m.main_group);
            }
          });
          
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


      {/* TEMPERATURE CHART */}
      <div 
        onClick={() => navigate('/chart')}
        className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl p-4 shadow-lg pointer-events-auto flex-1 flex flex-col min-h-0 transition-colors group"
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
                <YAxis stroke="#9ca3af" fontSize={10} domain={[0, 100]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', fontSize: '10px' }}
                  itemStyle={{ fontWeight: 'bold' }}
                  labelStyle={{ color: 'var(--text-secondary)' }}
                />
                <Legend verticalAlign="top" height={24} iconType="circle" wrapperStyle={{ fontSize: '10px' }} />
                
                <ReferenceLine y={60} stroke="#ef4444" strokeDasharray="5 5" label={{ position: 'insideTopLeft', value: 'WARN', fill: '#ef4444', fontSize: 9, fontWeight: 'bold' }} />
                
                {histGroups.map((name, i) => (
                  <Line key={name} type="monotone" dataKey={name} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={false} activeDot={{ r: 4, strokeWidth: 0 }} connectNulls={true} />
                ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </>
  );
}
