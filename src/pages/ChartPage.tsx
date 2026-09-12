import { useState, useEffect } from 'react';
import { LineChart as LineChartIcon, Filter, Download, Activity, Thermometer, AlertTriangle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine } from 'recharts';
import TopNavbar from '../components/layout/TopNavbar';

// Generate some rich dummy data for the chart (24 hours)
const generateHistoricalData = () => {
  const data = [];
  const now = new Date();
  now.setMinutes(0, 0, 0); // Start at top of hour

  for (let i = 24; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 60 * 60 * 1000);
    const hourStr = time.getHours().toString().padStart(2, '0') + ':00';
    
    // Simulate day/night temperature curves
    const baseTemp = 40 + Math.sin((time.getHours() / 24) * Math.PI * 2) * 10;
    
    data.push({
      time: hourStr,
      'TN BEK 3': Number((baseTemp + Math.random() * 5).toFixed(1)),
      'TN BEK 4': Number((baseTemp + 2 + Math.random() * 6).toFixed(1)),
      'TN TCM 1': Number((baseTemp - 5 + Math.random() * 4).toFixed(1)),
      'BC MAIN 01': Number((baseTemp + 15 + Math.random() * 10).toFixed(1)), // Hotter belt
    });
  }
  return data;
};

const CHART_DATA = generateHistoricalData();

export default function ChartPage() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true;
  });
  const [userRole, setUserRole] = useState('OPERATOR');
  const [userId, setUserId] = useState('OP-7729');
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');

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
            <p className="text-text-secondary font-mono mt-1">Detailed temperature analysis across all DTS segments</p>
          </div>

          <div className="flex space-x-3">
            <div className="flex bg-bg-panel border border-border rounded-lg overflow-hidden shadow-sm">
              {['1h', '6h', '24h', '7d', '30d'].map(range => (
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
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 shrink-0">
          <div className="bg-bg-panel border border-border rounded-xl p-5 flex items-center space-x-4 shadow-md">
            <div className="p-3 bg-scada-primary/20 text-scada-primary rounded-lg border border-scada-primary/30">
              <Activity size={24} />
            </div>
            <div>
              <p className="text-text-secondary text-xs font-bold tracking-widest uppercase">Avg Temperature</p>
              <p className="text-2xl font-mono font-bold">48.5<span className="text-lg text-text-secondary ml-1">°C</span></p>
            </div>
          </div>
          <div className="bg-bg-panel border border-border rounded-xl p-5 flex items-center space-x-4 shadow-md">
            <div className="p-3 bg-red-500/20 text-red-500 rounded-lg border border-red-500/30">
              <Thermometer size={24} />
            </div>
            <div>
              <p className="text-text-secondary text-xs font-bold tracking-widest uppercase">Max Recorded</p>
              <p className="text-2xl font-mono font-bold text-red-400">82.3<span className="text-lg text-red-400/50 ml-1">°C</span></p>
              <p className="text-[10px] text-text-secondary mt-1 font-mono">BC MAIN 01 at 14:00</p>
            </div>
          </div>
          <div className="bg-bg-panel border border-border rounded-xl p-5 flex items-center space-x-4 shadow-md">
            <div className="p-3 bg-blue-500/20 text-blue-500 rounded-lg border border-blue-500/30">
              <Thermometer size={24} />
            </div>
            <div>
              <p className="text-text-secondary text-xs font-bold tracking-widest uppercase">Min Recorded</p>
              <p className="text-2xl font-mono font-bold text-blue-400">32.1<span className="text-lg text-blue-400/50 ml-1">°C</span></p>
              <p className="text-[10px] text-text-secondary mt-1 font-mono">TN TCM 1 at 04:00</p>
            </div>
          </div>
          <div className="bg-bg-panel border border-border rounded-xl p-5 flex items-center space-x-4 shadow-md">
            <div className="p-3 bg-yellow-500/20 text-yellow-500 rounded-lg border border-yellow-500/30">
              <AlertTriangle size={24} />
            </div>
            <div>
              <p className="text-text-secondary text-xs font-bold tracking-widest uppercase">Alarm Triggers (24h)</p>
              <p className="text-2xl font-mono font-bold text-yellow-500">12</p>
            </div>
          </div>
        </div>

        {/* MAIN CHART */}
        <div className="bg-bg-panel border border-border rounded-xl p-6 flex-1 min-h-[400px] flex flex-col relative shadow-lg">
          <div className="absolute top-4 right-6 flex items-center space-x-4 z-10 bg-bg-panel/80 backdrop-blur-sm p-2 rounded-lg border border-border shadow-sm">
             <div className="flex items-center text-xs font-mono font-bold">
               <span className="w-3 h-3 rounded-full bg-red-500/50 border border-red-500 mr-2"></span>
               Alarm Threshold (70°C)
             </div>
             <div className="flex items-center text-xs font-mono font-bold">
               <span className="w-3 h-3 rounded-full bg-yellow-500/50 border border-yellow-500 mr-2"></span>
               Warning Threshold (60°C)
             </div>
          </div>

          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={CHART_DATA} margin={{ top: 20, right: 20, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" opacity={0.5} vertical={false} />
              
              <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" strokeWidth={2} label={{ position: 'insideTopLeft', value: 'ALARM', fill: '#ef4444', fontSize: 10, fontWeight: 'bold' }} />
              <ReferenceLine y={60} stroke="#eab308" strokeDasharray="3 3" strokeWidth={2} label={{ position: 'insideTopLeft', value: 'WARNING', fill: '#eab308', fontSize: 10, fontWeight: 'bold' }} />

              <XAxis 
                dataKey="time" 
                stroke="var(--text-secondary)" 
                fontSize={12} 
                tickMargin={15}
                tick={{ fill: 'var(--text-secondary)' }}
                axisLine={{ stroke: 'var(--border-color)' }}
                tickLine={false}
              />
              <YAxis 
                stroke="var(--text-secondary)" 
                fontSize={12} 
                tickFormatter={(value) => `${value}°C`}
                tick={{ fill: 'var(--text-secondary)' }}
                axisLine={false}
                tickLine={false}
                domain={[20, 90]}
              />
              
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'var(--bg-panel)', 
                  borderColor: 'var(--border-color)', 
                  borderRadius: '12px', 
                  boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)',
                  color: 'var(--text-primary)',
                  fontFamily: 'monospace'
                }}
                itemStyle={{ fontWeight: 'bold' }}
                labelStyle={{ color: 'var(--text-secondary)', marginBottom: '8px', borderBottom: '1px solid var(--border-color)', paddingBottom: '4px' }}
              />
              
              <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ paddingTop: '20px' }} />
              
              <Line type="monotone" dataKey="TN BEK 3" stroke="#0ea5e9" strokeWidth={3} dot={false} activeDot={{ r: 6, strokeWidth: 0 }} />
              <Line type="monotone" dataKey="TN BEK 4" stroke="#8b5cf6" strokeWidth={3} dot={false} activeDot={{ r: 6, strokeWidth: 0 }} />
              <Line type="monotone" dataKey="TN TCM 1" stroke="#10b981" strokeWidth={3} dot={false} activeDot={{ r: 6, strokeWidth: 0 }} />
              <Line type="monotone" dataKey="BC MAIN 01" stroke="#f97316" strokeWidth={3} dot={false} activeDot={{ r: 6, strokeWidth: 0 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
