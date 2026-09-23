import { useState, useEffect, useRef } from 'react';
import { LineChart as LineChartIcon, Download, Thermometer, Layers, Map, RefreshCw, XCircle, Activity } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine, AreaChart, Area } from 'recharts';
import { exportElementToPDF } from '../utils/exportPdf';
import TopNavbar from '../components/layout/TopNavbar';
import { invoke } from '@tauri-apps/api/core';
import { GROUP_COLORS, CHART_COLORS_FALLBACK } from '../data/constants';

type ChartMode = 'history' | 'spatial';

export default function ChartPage() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true;
  });
  const [userRole, setUserRole] = useState('OPERATOR');
  const [userId, setUserId] = useState('OP-7729');
  
  const [chartMode, setChartMode] = useState<ChartMode>('history');
  const [histSummary, setHistSummary] = useState<any>(null);
  
  // Format today's date as YYYY-MM-DD (Local Timezone safe)
  const today = new Date().toLocaleDateString('sv');
  
  // Filter Inputs (Not yet applied)
  const [filterDate, setFilterDate] = useState<string>(today);
  const [filterStartTime, setFilterStartTime] = useState<string>(() => {
    const d = new Date();
    d.setHours(d.getHours() - 1);
    return d.toTimeString().substring(0, 5);
  });
  const [filterEndTime, setFilterEndTime] = useState<string>(() => {
    return new Date().toTimeString().substring(0, 5);
  });
  
  // History Mode State (Displayed Data)
  const [histData, setHistData] = useState<any[]>([]);
  const [histGroups, setHistGroups] = useState<string[]>([]);
  
  // Spatial Mode State
  const [mappings, setMappings] = useState<any[]>([]);
  const [selectedGroup, setSelectedGroup] = useState<string>('');
  
  const [warningThreshold, setWarningThreshold] = useState(45);
  const [criticalThreshold, setCriticalThreshold] = useState(60);
  const [spatialData, setSpatialData] = useState<any[]>([]);
  
  const [loading, setLoading] = useState(false); // Default false, only true when explicitly fetching
  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [stats, setStats] = useState({ max: 0, avg: 0, min: 0 });

  // Abort control ref
  const fetchAbortRef = useRef<boolean>(false);

  useEffect(() => {
    const role = localStorage.getItem('userRole');
    const id = localStorage.getItem('userId');
    if (role) setUserRole(role);
    if (id) setUserId(id);
    invoke<Record<string, string>>("get_all_settings").then(settings => {
      if (settings["warning_threshold"]) setWarningThreshold(Number(settings["warning_threshold"]));
      if (settings["critical_threshold"]) setCriticalThreshold(Number(settings["critical_threshold"]));
    }).catch(console.error);
    
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

  // Expose fetch function so we can call it initially and on button click
  const fetchData = async () => {
    if (!('__TAURI_INTERNALS__' in window)) return;
    
    try {
      fetchAbortRef.current = false;
      setLoading(true);
      setHasError(false);
      
      if (chartMode === 'history') {
        const start_dt = `${filterDate} ${filterStartTime}:00`;
        const end_dt = `${filterDate} ${filterEndTime}:59`;
        
        const [data, mappingsData, summary] = await Promise.all([
           invoke<any[]>('get_groups_history', { startDt: start_dt, endDt: end_dt }),
           invoke<any[]>('get_segment_mappings'),
           invoke<any>('get_history_summary', { startDt: start_dt, endDt: end_dt }).catch(e => { console.error(e); return null; })
        ]);
        setHistSummary(summary);
        
        if (fetchAbortRef.current) return;
        
        if (data.length === 0) {
          setHistData([]);
          setHistGroups([]);
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
        
        setHistGroups(Array.from(groupsSet));
        setHistData(flatData);
        
      } else {
        if (!selectedGroup) {
          setLoading(false);
          return;
        }
        const data = await invoke<any[]>('get_spatial_profile', { mainGroup: selectedGroup });
        if (fetchAbortRef.current) return;
        
        setSpatialData(data);
        if (data.length > 0) {
          const temps = data.map(d => d.temp).filter(t => t > 0);
          if (temps.length > 0) {
            setStats({
              max: Math.max(...temps),
              min: Math.min(...temps),
              avg: temps.reduce((a,b) => a+b, 0) / temps.length
            });
          }
        } else {
          setStats({ max: 0, min: 0, avg: 0 });
        }
      }
      
      setLoading(false);
    } catch (err) {
      if (fetchAbortRef.current) return;
      console.error(err);
      setHasError(true);
      setErrorMessage(typeof err === 'string' ? err : JSON.stringify(err));
      setLoading(false);
    }
  };

  // Initial fetch on mount or mode change
  useEffect(() => {
    fetchData();
    return () => { fetchAbortRef.current = true; };
  }, [chartMode, selectedGroup]);

  const handleCancel = () => {
    fetchAbortRef.current = true;
    setLoading(false);
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-bg-panel/95 backdrop-blur border border-border p-3 rounded-lg shadow-xl">
          <p className="text-text-primary font-bold mb-2 border-b border-border pb-1">
            {chartMode === 'history' ? `Time: ${label}` : `Distance: ${label}m`}
          </p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center justify-between space-x-4 mb-1">
              <span style={{ color: entry.color }} className="font-bold text-xs uppercase">
                {entry.name}
              </span>
              <span className="font-mono text-sm text-text-primary font-bold">
                {entry.value ? entry.value.toFixed(1) : '--'}°C
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  const uniqueGroups = Array.from(new Set(mappings.map(m => m.main_group))).filter(g => g !== 'Unassigned') as string[];

  return (
    <div className="h-screen w-full bg-bg-base flex flex-col font-sans overflow-hidden text-text-primary transition-colors duration-200">
      <TopNavbar 
        isFullscreen={false}
        isDarkMode={isDarkMode} 
        setIsDarkMode={setIsDarkMode} 
        userRole={userRole}
        userId={userId}
      />

      <div className="flex-1 flex flex-col p-4 md:p-6 space-y-4 overflow-y-auto">
        <div className="flex flex-col md:flex-row md:items-center justify-between">
          <div className="flex items-center text-scada-primary mb-4 md:mb-0">
            <LineChartIcon size={28} className="mr-3" />
            <h1 className="text-2xl font-bold tracking-widest">DATA ANALYTICS</h1>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="flex bg-bg-surface p-1 rounded-lg border border-border">
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
                <input type="date" value={filterDate} onChange={e => setFilterDate(e.target.value)} className="bg-bg-surface border border-border rounded px-2 py-1 text-xs text-text-primary outline-none" />
                
                <span className="text-xs font-bold text-text-secondary ml-2">FROM:</span>
                <input type="time" value={filterStartTime} onChange={e => setFilterStartTime(e.target.value)} className="bg-bg-surface border border-border rounded px-2 py-1 text-xs text-text-primary outline-none" />
                
                <span className="text-xs font-bold text-text-secondary ml-2">TO:</span>
                <input type="time" value={filterEndTime} onChange={e => setFilterEndTime(e.target.value)} className="bg-bg-surface border border-border rounded px-2 py-1 text-xs text-text-primary outline-none" />
                
                {loading ? (
                  <button onClick={handleCancel} className="ml-2 flex items-center px-3 py-1 bg-red-500/20 text-red-500 hover:bg-red-500/30 rounded border border-red-500/30 font-bold text-xs transition-colors">
                    <XCircle size={14} className="mr-1 animate-pulse" /> CANCEL
                  </button>
                ) : (
                  <button onClick={fetchData} className="ml-2 flex items-center px-3 py-1 bg-scada-primary text-white hover:bg-scada-primary/80 rounded border border-scada-primary font-bold text-xs transition-colors shadow-[0_0_10px_rgba(59,130,246,0.3)]">
                    <RefreshCw size={14} className="mr-1" /> APPLY
                  </button>
                )}
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

        {/* SUMMARY STATS FOR SPATIAL */}
        {chartMode === 'spatial' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-bg-panel border border-border rounded-xl p-4 flex items-center shadow-sm">
              <div className="p-3 bg-red-500/20 rounded-lg text-red-500 mr-4">
                <Thermometer size={24} />
              </div>
              <div>
                <p className="text-sm font-mono text-text-secondary">MAX TEMPERATURE</p>
                <p className="text-2xl font-bold text-red-500">{stats.max.toFixed(1)}°C</p>
              </div>
            </div>
            
            <div className="bg-bg-panel border border-border rounded-xl p-4 flex items-center shadow-sm">
              <div className="p-3 bg-blue-500/20 rounded-lg text-blue-500 mr-4">
                <Thermometer size={24} />
              </div>
              <div>
                <p className="text-sm font-mono text-text-secondary">MIN TEMPERATURE</p>
                <p className="text-2xl font-bold text-blue-500">{stats.min.toFixed(1)}°C</p>
              </div>
            </div>
            
            <div className="bg-bg-panel border border-border rounded-xl p-4 flex items-center shadow-sm">
              <div className="p-3 bg-green-500/20 rounded-lg text-green-500 mr-4">
                <Activity size={24} />
              </div>
              <div>
                <p className="text-sm font-mono text-text-secondary">AVG TEMPERATURE</p>
                <p className="text-2xl font-bold text-green-500">{stats.avg.toFixed(1)}°C</p>
              </div>
            </div>
          </div>
        )}

        {/* CHART AREA */}
        <div id="chart-export-container" className="flex-1 bg-bg-panel border border-border rounded-xl p-4 flex flex-col relative shadow-sm">
          {hasError ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <p className="text-scada-error font-mono mb-2">DATABASE CONNECTION ERROR</p>
                <p className="text-text-secondary text-sm">{errorMessage}</p>
              </div>
            </div>
          ) : (
            chartMode === 'history' ? (
              <div className="flex flex-col h-full">
                {histSummary && (
                  <div className="flex gap-4 mb-4 shrink-0 overflow-x-auto">
                    <div className="bg-bg-surface border border-red-500/30 p-3 rounded-lg flex-1 min-w-[200px] flex items-center shadow-[0_0_15px_rgba(239,68,68,0.1)]">
                      <Thermometer className="text-red-500 mr-3 shrink-0" size={24} />
                      <div>
                        <div className="text-xs text-text-secondary font-bold tracking-wider">HIGHEST TEMP</div>
                        <div className="text-red-500 font-bold text-lg">{histSummary.max_temp.toFixed(1)}°C <span className="text-sm font-normal text-text-secondary">at {histSummary.max_time}</span></div>
                        <div className="text-xs font-mono text-text-secondary truncate" title={histSummary.max_segment}>{histSummary.max_group} - {histSummary.max_segment}</div>
                      </div>
                    </div>
                    <div className="bg-bg-surface border border-blue-500/30 p-3 rounded-lg flex-1 min-w-[200px] flex items-center shadow-[0_0_15px_rgba(59,130,246,0.1)]">
                      <Thermometer className="text-blue-500 mr-3 shrink-0" size={24} />
                      <div>
                        <div className="text-xs text-text-secondary font-bold tracking-wider">LOWEST TEMP</div>
                        <div className="text-blue-500 font-bold text-lg">{histSummary.min_temp.toFixed(1)}°C <span className="text-sm font-normal text-text-secondary">at {histSummary.min_time}</span></div>
                        <div className="text-xs font-mono text-text-secondary truncate" title={histSummary.min_segment}>{histSummary.min_group} - {histSummary.min_segment}</div>
                      </div>
                    </div>
                  </div>
                )}
                <div className="flex-1 min-h-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={histData} margin={{ top: 10, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke={isDarkMode ? '#333' : '#eee'} vertical={false} />
                      <XAxis dataKey="time" stroke={isDarkMode ? '#888' : '#666'} tick={{ fill: isDarkMode ? '#888' : '#666' }} />
                      <YAxis stroke={isDarkMode ? '#888' : '#666'} tick={{ fill: isDarkMode ? '#888' : '#666' }} domain={[0, 100]} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ paddingTop: '20px' }} />
                  <ReferenceLine y={criticalThreshold} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'insideTopLeft', value: 'CRITICAL', fill: '#ef4444', fontSize: 12 }} />
                  <ReferenceLine y={warningThreshold} stroke="#eab308" strokeDasharray="3 3" label={{ position: 'insideTopLeft', value: 'WARNING', fill: '#eab308', fontSize: 12 }} />
                  
                  {histGroups.map((name, i) => (
                    <Line key={name} type="monotone" dataKey={name} stroke={GROUP_COLORS[name] || CHART_COLORS_FALLBACK[i % CHART_COLORS_FALLBACK.length]} strokeWidth={2} dot={false} activeDot={{ r: 6, strokeWidth: 0 }} connectNulls={true} />
                  ))}
                </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            ) : (
              (() => {
                const dynamicColor = stats.max >= criticalThreshold ? '#ef4444' : (stats.max >= warningThreshold ? '#eab308' : '#10b981');
                return (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={spatialData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                      <defs>
                        <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor={dynamicColor} stopOpacity={0.8}/>
                          <stop offset="95%" stopColor={dynamicColor} stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke={isDarkMode ? '#333' : '#eee'} vertical={false} />
                      <XAxis dataKey="distance" stroke={isDarkMode ? '#888' : '#666'} tick={{ fill: isDarkMode ? '#888' : '#666' }} />
                      <YAxis stroke={isDarkMode ? '#888' : '#666'} tick={{ fill: isDarkMode ? '#888' : '#666' }} domain={[0, 100]} />
                      <Tooltip content={<CustomTooltip />} />
                      <ReferenceLine y={criticalThreshold} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'insideTopLeft', value: 'CRITICAL', fill: '#ef4444', fontSize: 12 }} />
                      <ReferenceLine y={warningThreshold} stroke="#eab308" strokeDasharray="3 3" label={{ position: 'insideTopLeft', value: 'WARNING', fill: '#eab308', fontSize: 12 }} />
                      <Area type="monotone" dataKey="temp" stroke={dynamicColor} fillOpacity={1} fill="url(#colorTemp)" isAnimationActive={false} />
                    </AreaChart>
                  </ResponsiveContainer>
                );
              })()
            )
          )}
          
          {/* Overlay Loading Effect - Only dims the chart, data remains visible behind it! */}
          {loading && (
            <div className="absolute inset-0 bg-bg-base/40 backdrop-blur-[1px] flex flex-col items-center justify-center z-10 rounded-xl transition-all duration-300">
               <RefreshCw size={36} className="text-scada-primary animate-spin mb-2" />
               <p className="font-mono text-sm font-bold text-scada-primary animate-pulse tracking-widest">FETCHING DATA...</p>
            </div>
          )}
          
        </div>
      </div>
    </div>
  );
}
