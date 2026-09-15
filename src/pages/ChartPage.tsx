import { useState, useEffect } from 'react';
import { LineChart as LineChartIcon, Filter, Download, Activity, Thermometer, AlertTriangle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine } from 'recharts';
import TopNavbar from '../components/layout/TopNavbar';
import { invoke } from '@tauri-apps/api/core';

const COLORS = ['#06b6d4', '#eab308', '#ef4444', '#10b981', '#a855f7'];

export default function ChartPage() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true;
  });
  const [userRole, setUserRole] = useState('OPERATOR');
  const [userId, setUserId] = useState('OP-7729');
  const [selectedTimeRange, setSelectedTimeRange] = useState('30m'); 
  
  const [chartData, setChartData] = useState<any[]>([]);
  const [lines, setLines] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [stats, setStats] = useState({ max: 0, avg: 0, min: 0 });

  useEffect(() => {
    const role = localStorage.getItem('userRole');
    const id = localStorage.getItem('userId');
    if (role) setUserRole(role);
    if (id) setUserId(id);
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
        // Fetch active mappings
        const mappings: any[] = await invoke('get_live_segments');
        
        if (!mappings || mappings.length === 0) {
          if (isMounted) setLoading(false);
          return;
        }

        // Take top 5 hottest segments
        const top5 = [...mappings].sort((a: any, b: any) => (b.temp_avg || 0) - (a.temp_avg || 0)).slice(0, 5);
        const names = top5.map((m: any) => m.custom_name || m.original_name || `CH${m.dts_ch}-C${m.dts_code}`);
        if (isMounted) setLines(names);
        
        const limit = selectedTimeRange === '30m' ? 30 : selectedTimeRange === '1h' ? 60 : selectedTimeRange === '6h' ? 360 : 30;
        
        // Fetch history for each
        const histories = await Promise.all(
          top5.map((m: any) => invoke<any[]>('get_segment_history', { dtsCh: m.dts_ch, dtsCode: m.dts_code, limit }))
        );
        
        // Merge by time
        const mergedMap: Record<string, any> = {};
        histories.forEach((hist, idx) => {
          const segName = names[idx];
          hist.forEach(pt => {
            if (!mergedMap[pt.time]) mergedMap[pt.time] = { time: pt.time };
            mergedMap[pt.time][segName] = pt.temp;
          });
        });
        
        const finalData = Object.values(mergedMap).sort((a: any, b: any) => a.time.localeCompare(b.time));
        
        if (isMounted) {
          setChartData(finalData);
          
          let max = -999, min = 999, sum = 0, count = 0;
          finalData.forEach(row => {
            names.forEach(n => {
              if (row[n] !== undefined) {
                if (row[n] > max) max = row[n];
                if (row[n] < min) min = row[n];
                sum += row[n];
                count++;
              }
            });
          });
          setStats({ max: max === -999 ? 0 : max, min: min === 999 ? 0 : min, avg: count ? sum / count : 0 });
          setHasError(false);
          setLoading(false);
        }
      } catch (err) {
        console.error(err);
        if (isMounted) {
          setHasError(true);
          setLoading(false);
        }
      }
    };
    
    fetchData();
    const interval = setInterval(fetchData, 10000); 
    return () => { isMounted = false; clearInterval(interval); };
  }, [selectedTimeRange]);

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
              HISTORICAL TREND ANALYSIS
            </h2>
            <p className="text-text-secondary font-mono mt-1">Showing top 5 hottest active segments</p>
          </div>

          <div className="flex space-x-3">
            <div className="flex bg-bg-panel border border-border rounded-lg overflow-hidden shadow-sm">
              {['30m', '1h', '6h'].map(range => (
                <button
                  key={range}
                  onClick={() => setSelectedTimeRange(range)}
                  className={`px-4 py-2 font-mono text-sm font-bold transition-colors ${
                    selectedTimeRange === range 
                      ? 'bg-scada-primary/20 text-scada-primary border-b-2 border-scada-primary' 
                      : 'text-text-secondary hover:bg-bg-surface hover:text-text-primary border-b-2 border-transparent'
                  }`}
                >
                  {range}
                </button>
              ))}
            </div>
            
            <button className="flex items-center px-4 py-2 bg-bg-panel border border-border rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-surface transition-colors font-bold text-sm shadow-sm">
              <Filter size={16} className="mr-2" /> FILTER SEGMENTS
            </button>
            <button className="flex items-center px-4 py-2 bg-bg-panel border border-border rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-surface transition-colors font-bold text-sm shadow-sm">
              <Download size={16} className="mr-2" /> EXPORT CSV
            </button>
          </div>
        </div>

        {/* SUMMARY STATS */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-bg-panel border border-border rounded-xl p-4 flex items-center shadow-sm">
            <div className="p-3 bg-red-500/20 rounded-lg text-red-500 mr-4">
              <Thermometer size={24} />
            </div>
            <div>
              <p className="text-xs text-text-secondary uppercase tracking-widest font-bold">System Peak Temp</p>
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
          
          <div className="bg-bg-panel border border-border rounded-xl p-4 flex items-center shadow-sm">
            <div className="p-3 bg-yellow-500/20 rounded-lg text-yellow-500 mr-4">
              <AlertTriangle size={24} />
            </div>
            <div>
              <p className="text-xs text-text-secondary uppercase tracking-widest font-bold">Active Alarms</p>
              <p className="text-2xl font-mono font-bold text-yellow-500">0<span className="text-lg text-yellow-500/50 ml-1">Events</span></p>
            </div>
          </div>
        </div>

        {/* MAIN CHART */}
        <div className="flex-1 bg-bg-panel border border-border rounded-xl p-6 shadow-sm flex flex-col min-h-[400px]">
          {loading && chartData.length === 0 ? (
            <div className="flex-1 flex items-center justify-center font-mono text-scada-primary animate-pulse tracking-widest font-bold">LOADING HISTORICAL DATA...</div>
          ) : (!loading && hasError && chartData.length === 0) ? (
            <div className="flex-1 flex items-center justify-center font-mono text-red-500 tracking-widest font-bold animate-pulse text-center">
              CONNECTION ERROR.<br/>RETRYING...
            </div>
          ) : (!loading && !hasError && chartData.length === 0) ? (
            <div className="flex-1 flex items-center justify-center font-mono text-red-400 tracking-widest font-bold text-center">
              NO SEGMENTS FOUND.<br/>PLEASE SYNC FROM DTS IN SETTINGS.
            </div>
          ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" opacity={0.3} vertical={false} />
              <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} tickMargin={10} />
              <YAxis stroke="#9ca3af" fontSize={12} domain={['dataMin - 10', 'dataMax + 10']} />
              <Tooltip 
                contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', fontSize: '12px' }}
                itemStyle={{ fontWeight: 'bold' }}
                labelStyle={{ color: 'var(--text-secondary)' }}
              />
              <Legend verticalAlign="top" height={36} iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
              
              <ReferenceLine y={60} stroke="#ef4444" strokeDasharray="5 5" label={{ position: 'insideTopLeft', value: 'WARNING THRESHOLD', fill: '#ef4444', fontSize: 10, fontWeight: 'bold' }} />
              
              {lines.map((name, i) => (
                <Line key={name} type="monotone" dataKey={name} stroke={COLORS[i % COLORS.length]} strokeWidth={name === lines[0] ? 3 : 2} dot={false} activeDot={{ r: 6, strokeWidth: 0 }} />
              ))}
            </LineChart>
          </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}
