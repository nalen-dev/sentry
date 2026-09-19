import { useState, useEffect, useMemo } from 'react';
import { LineChart as LineChartIcon, Download, Activity, Thermometer, Layers, Map } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine, AreaChart, Area } from 'recharts';
import { exportElementToPDF } from '../utils/exportPdf';
import TopNavbar from '../components/layout/TopNavbar';
import { invoke } from '@tauri-apps/api/core';

const COLORS = ['#06b6d4', '#eab308', '#ef4444', '#10b981', '#a855f7', '#f97316', '#ec4899', '#3b82f6'];

type ChartMode = 'history' | 'spatial';

export default function ChartPage() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true;
  });
  const [userRole, setUserRole] = useState('OPERATOR');
  const [userId, setUserId] = useState('OP-7729');
  
  const [chartMode, setChartMode] = useState<ChartMode>('history');
  
  // History Mode State
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [timeRangeHours, setTimeRangeHours] = useState(24); 
  const [histData, setHistData] = useState<any[]>([]);
  const [histGroups, setHistGroups] = useState<string[]>([]);
  
  // Spatial Mode State
  const [mappings, setMappings] = useState<any[]>([]);
  const [selectedGroup, setSelectedGroup] = useState<string>('');
  const [spatialData, setSpatialData] = useState<any[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [stats, setStats] = useState({ max: 0, avg: 0, min: 0 });

  useEffect(() => {
    const role = localStorage.getItem('userRole');
    const id = localStorage.getItem('userId');
    if (role) setUserRole(role);
    if (id) setUserId(id);
    
    // Load mappings once for Spatial mode dropdown
    if ('__TAURI_INTERNALS__' in window) {
      invoke<any[]>('get_live_segments').then(m => {
        setMappings(m);
        const uniqueGroups = Array.from(new Set(m.map((x: any) => x.main_group))).filter(g => g !== 'Unassigned') as string[];
        if (uniqueGroups.length > 0) setSelectedGroup(uniqueGroups[0]);
      }).catch(console.error);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    document.documentElement.className = isDarkMode ? 'dark' : 'light';
  }, [isDarkMode]);

  useEffect(() => {
    let isMounted = true;
    
    const fetchData = async () => {
      if (!('__TAURI_INTERNALS__' in window)) return;
      
      try {
        setLoading(true);
        
        if (chartMode === 'history') {
          const minutes = timeRangeHours * 60;
          const [data, mappingsData] = await Promise.all([
             invoke<any[]>('get_groups_history', { minutes }),
             invoke<any[]>('get_segment_mappings')
          ]);
          
          if (!isMounted) return;
          
          if (data.length === 0) {
            setHistData([]);
            setHasError(false);
            setLoading(false);
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
          
          const groups = Array.from(groupsSet).sort();
          setHistGroups(groups);
          setHistData(flatData);
          
          // Calc stats
          let max = -999, min = 999, sum = 0, count = 0;
          flatData.forEach(row => {
            groups.forEach(g => {
              if (row[g] !== undefined) {
                if (row[g] > max) max = row[g];
                if (row[g] < min) min = row[g];
                sum += row[g];
                count++;
              }
            });
          });
          setStats({ max: max === -999 ? 0 : max, min: min === 999 ? 0 : min, avg: count ? sum / count : 0 });
          setHasError(false);
          setLoading(false);
          
        } else {
          // Spatial Mode
          if (!selectedGroup) {
            setLoading(false);
            return;
          }
          
          const groupSegments = mappings.filter(m => m.main_group === selectedGroup);
          if (groupSegments.length === 0) {
            setSpatialData([]);
            setLoading(false);
            return;
          }
          
          // All segments in a group must share the same dts_ch.
          const ch = groupSegments[0].dts_ch;
          let minM = 999999, maxM = 0;
          groupSegments.forEach(s => {
            if (s.start_m !== null && s.start_m < minM) minM = s.start_m;
            if (s.end_m !== null && s.end_m > maxM) maxM = s.end_m;
          });
          
          const safeMin = minM === 999999 ? 0 : minM;
          const safeMax = maxM === 0 ? 999999 : maxM;
          
          const curve: any[] = await invoke('get_segment_curve', { dtsCh: ch, startM: safeMin, endM: safeMax });
          
          if (!isMounted) return;
          
          if (curve.length === 0) {
            setSpatialData([]);
            setHasError(false);
            setLoading(false);
            return;
          }
          
          // Filter out error codes from Rust (< 0)
          const sliced = curve.filter(pt => pt.temp >= 0);
          setSpatialData(sliced);
          
          let max = -999, min = 999, sum = 0, count = 0;
          sliced.forEach(pt => {
            if (pt.temp > max) max = pt.temp;
            if (pt.temp < min) min = pt.temp;
            sum += pt.temp;
            count++;
          });
          setStats({ max: max === -999 ? 0 : max, min: min === 999 ? 0 : min, avg: count ? sum / count : 0 });
          setHasError(false);
          setLoading(false);
        }
        
      } catch (err) {
        console.error(err);
        if (isMounted) {
          setHasError(true);
          setErrorMessage(typeof err === 'string' ? err : JSON.stringify(err));
          setLoading(false);
        }
      }
    };
    
    fetchData();
    const interval = setInterval(fetchData, 10000); 
    return () => { isMounted = false; clearInterval(interval); };
  }, [selectedDate, timeRangeHours, chartMode, selectedGroup, mappings]);

  const uniqueGroups = useMemo(() => Array.from(new Set(mappings.map(m => m.main_group))).filter(g => g !== 'Unassigned') as string[], [mappings]);

  return (
    <div className="flex flex-col h-screen bg-bg-base text-text-primary overflow-hidden font-sans">
      <TopNavbar 
        isFullscreen={false}
        isDarkMode={isDarkMode}
        setIsDarkMode={setIsDarkMode}
        userRole={userRole}
        userId={userId}
      />

      <div className="flex-1 overflow-y-auto p-6 flex flex-col space-y-6">
        {/* HEADER & CONTROLS */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
          <div>
            <h2 className="text-2xl font-bold tracking-widest text-text-primary flex items-center">
              <LineChartIcon className="mr-3 text-scada-primary" size={28} /> 
              DATA ANALYTICS
            </h2>
            <p className="text-text-secondary font-mono mt-1">
              {chartMode === 'history' ? 'Average Temperature of each Group over time' : `Temperature Profile across distance for Group`}
            </p>
          </div>

          <div className="flex space-x-3">
            <div className="flex bg-bg-panel border border-border rounded-lg overflow-hidden shadow-sm mr-4">
              <button
                onClick={() => setChartMode('history')}
                className={`flex items-center px-4 py-2 font-mono text-sm font-bold transition-colors ${
                  chartMode === 'history' ? 'bg-scada-primary/20 text-scada-primary border-b-2 border-scada-primary' : 'text-text-secondary hover:bg-bg-surface hover:text-text-primary border-b-2 border-transparent'
                }`}
              >
                <Layers size={16} className="mr-2" /> GROUP HISTORY
              </button>
              <button
                onClick={() => setChartMode('spatial')}
                className={`flex items-center px-4 py-2 font-mono text-sm font-bold transition-colors ${
                  chartMode === 'spatial' ? 'bg-scada-primary/20 text-scada-primary border-b-2 border-scada-primary' : 'text-text-secondary hover:bg-bg-surface hover:text-text-primary border-b-2 border-transparent'
                }`}
              >
                <Map size={16} className="mr-2" /> SPATIAL PROFILE
              </button>
            </div>
            
            {chartMode === 'history' ? (
              <div className="flex bg-bg-panel border border-border rounded-lg overflow-hidden shadow-sm items-center px-2 py-1 space-x-2">
                <span className="text-xs font-bold text-text-secondary">DATE:</span>
                <input type="date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)} className="bg-bg-surface border border-border rounded px-2 py-1 text-xs text-text-primary outline-none" />
                <span className="text-xs font-bold text-text-secondary ml-2">RANGE:</span>
                <input type="number" min="1" max="24" value={timeRangeHours} onChange={e => setTimeRangeHours(parseInt(e.target.value) || 1)} className="w-16 bg-bg-surface border border-border rounded px-2 py-1 text-xs text-text-primary outline-none" title="Hours" />
                <span className="text-xs font-mono text-text-secondary">Hours</span>
              </div>
            ) : (
              <select 
                className="bg-bg-panel border border-border rounded-lg px-4 py-2 text-sm font-bold text-text-primary outline-none focus:border-scada-primary shadow-sm uppercase tracking-widest"
                value={selectedGroup}
                onChange={e => setSelectedGroup(e.target.value)}
              >
                {uniqueGroups.map(g => (
                  <option key={g} value={g}>{g}</option>
                ))}
              </select>
            )}
            
            <button onClick={() => exportElementToPDF('chart-export-container', `DTS_Chart_${chartMode}_${new Date().getTime()}`)} className="flex items-center px-4 py-2 bg-bg-panel border border-border rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-surface transition-colors font-bold text-sm shadow-sm">
              <Download size={16} className="mr-2" /> EXPORT PDF
            </button>
          </div>
        </div>

        {/* SUMMARY STATS */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-bg-panel border border-border rounded-xl p-4 flex items-center shadow-sm">
            <div className="p-3 bg-red-500/20 rounded-lg text-red-500 mr-4">
              <Thermometer size={24} />
            </div>
            <div>
              <p className="text-xs text-text-secondary uppercase tracking-widest font-bold">Peak Temp</p>
              <p className="text-2xl font-mono font-bold text-red-500">{stats.max.toFixed(1)}°C</p>
            </div>
          </div>
          
          <div className="bg-bg-panel border border-border rounded-xl p-4 flex items-center shadow-sm">
            <div className="p-3 bg-scada-primary/20 rounded-lg text-scada-primary mr-4">
              <Activity size={24} />
            </div>
            <div>
              <p className="text-xs text-text-secondary uppercase tracking-widest font-bold">Average Temp</p>
              <p className="text-2xl font-mono font-bold text-text-primary">{stats.avg.toFixed(1)}°C</p>
            </div>
          </div>

          <div className="bg-bg-panel border border-border rounded-xl p-4 flex items-center shadow-sm">
            <div className="p-3 bg-blue-500/20 rounded-lg text-blue-500 mr-4">
              <Thermometer size={24} />
            </div>
            <div>
              <p className="text-xs text-text-secondary uppercase tracking-widest font-bold">Minimum Temp</p>
              <p className="text-2xl font-mono font-bold text-text-primary">{stats.min.toFixed(1)}°C</p>
            </div>
          </div>
        </div>

        {/* MAIN CHART */}
        <div className="flex-1 bg-bg-panel border border-border rounded-xl p-6 shadow-sm flex flex-col min-h-[400px]">
          {loading && ((chartMode === 'history' && histData.length === 0) || (chartMode === 'spatial' && spatialData.length === 0)) ? (
            <div className="flex-1 flex items-center justify-center font-mono text-scada-primary animate-pulse tracking-widest font-bold">LOADING DATA...</div>
          ) : (!loading && hasError) ? (
            <div className="flex-1 flex items-center justify-center font-mono text-red-500 tracking-widest font-bold animate-pulse text-center">
              CONNECTION ERROR.<br/>RETRYING...<br/><span className="text-xs text-red-400 mt-2 block">{errorMessage}</span>
            </div>
          ) : (!loading && !hasError && chartMode === 'history' && histData.length === 0) || (!loading && !hasError && chartMode === 'spatial' && spatialData.length === 0) ? (
            <div className="flex-1 flex items-center justify-center font-mono text-red-400 tracking-widest font-bold text-center">
              NO SEGMENTS OR DATA FOUND.<br/>PLEASE SYNC FROM DTS IN SETTINGS.
            </div>
          ) : (
          <ResponsiveContainer width="100%" height="100%">
            {chartMode === 'history' ? (
              <LineChart data={histData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" opacity={0.3} vertical={false} />
                <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} tickMargin={10} />
                <YAxis stroke="#9ca3af" fontSize={12} domain={[0, 100]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', fontSize: '12px' }}
                  itemStyle={{ fontWeight: 'bold' }}
                  labelStyle={{ color: 'var(--text-secondary)' }}
                />
                <Legend verticalAlign="top" height={36} iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
                
                
                <ReferenceLine y={45} stroke="#eab308" strokeDasharray="5 5" label={{ position: 'insideTopLeft', value: 'WARNING THRESHOLD', fill: '#eab308', fontSize: 10, fontWeight: 'bold' }} />
                <ReferenceLine y={60} stroke="#ef4444" strokeDasharray="5 5" label={{ position: 'insideTopLeft', value: 'DANGER THRESHOLD', fill: '#ef4444', fontSize: 10, fontWeight: 'bold' }} />

                
                {histGroups.map((name, i) => (
                  <Line key={name} type="monotone" dataKey={name} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={false} activeDot={{ r: 6, strokeWidth: 0 }} connectNulls={true} />
                ))}
              </LineChart>
            ) : (
              (() => {
                const dynamicColor = stats.max >= 60 ? '#ef4444' : (stats.max >= 45 ? '#eab308' : '#10b981');
                return (
                  <AreaChart data={spatialData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={dynamicColor} stopOpacity={0.8}/>
                        <stop offset="95%" stopColor={dynamicColor} stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" opacity={0.3} vertical={false} />
                    <XAxis dataKey="distance" stroke="#9ca3af" fontSize={12} tickMargin={10} tickFormatter={(v) => `${v}m`} />
                    <YAxis stroke="#9ca3af" fontSize={12} domain={[0, 100]} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', fontSize: '12px' }}
                      itemStyle={{ color: dynamicColor, fontWeight: 'bold' }}
                      labelStyle={{ color: 'var(--text-secondary)' }}
                      labelFormatter={(v) => `Distance: ${v} meters`}
                    />
                    
                    <ReferenceLine y={45} stroke="#eab308" strokeDasharray="5 5" label={{ position: 'insideTopLeft', value: 'WARNING THRESHOLD', fill: '#eab308', fontSize: 10, fontWeight: 'bold' }} />
                    <ReferenceLine y={60} stroke="#ef4444" strokeDasharray="5 5" label={{ position: 'insideTopLeft', value: 'DANGER THRESHOLD', fill: '#ef4444', fontSize: 10, fontWeight: 'bold' }} />
                    
                    <Area type="monotone" dataKey="temp" name="Temperature (°C)" stroke={dynamicColor} strokeWidth={2} fillOpacity={1} fill="url(#colorTemp)" />
                  </AreaChart>
                );
              })()
            )}
          </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}
