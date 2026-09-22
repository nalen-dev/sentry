import re

with open('src/pages/LogsPage.tsx', 'r') as f:
    content = f.read()

# I will completely replace LogsPage.tsx to cleanly implement the tabs and fetch logic
new_logs = """import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { exportElementToPDF } from '../utils/exportPdf';
import { History, Download, AlertTriangle, Info, AlertCircle, Search, FileText, Server, Settings, Power, LogIn } from 'lucide-react';
import TopNavbar from '../components/layout/TopNavbar';

interface HardwareLog {
  id: string;
  type: 'info' | 'warn' | 'error';
  timestamp: Date;
  segment: string;
  msg: string;
  user: string;
}

interface SystemLog {
  id: number;
  timestamp: string;
  event_type: string;
  message: string;
}

export default function LogsPage() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true;
  });
  const [userRole, setUserRole] = useState('OPERATOR');
  const [userId, setUserId] = useState('OP-7729');
  
  const [logMode, setLogMode] = useState<'hardware' | 'system'>('hardware');
  
  const [hwLogs, setHwLogs] = useState<HardwareLog[]>([]);
  const [sysLogs, setSysLogs] = useState<SystemLog[]>([]);
  
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'info' | 'warn' | 'error' | 'CONFIG' | 'SYSTEM' | 'ALARM' | 'AUTH'>('all');

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
    const fetchLogs = async () => {
      try {
        setLoading(true);
        if (logMode === 'hardware') {
          const dateParam = selectedDate ? selectedDate : null;
          const alarms: any[] = await invoke('get_alarms', { date: dateParam });
          const mappings: any[] = await invoke('get_segment_mappings');
          
          if (!isMounted) return;

          const mappedLogs: HardwareLog[] = alarms.map((a: any) => {
            const map = mappings.find(m => m.dts_ch === a.ch && m.dts_code === a.code);
            const segmentName = map && map.main_group !== 'Unassigned' ? `${map.main_group} ${map.sub_group ? '- ' + map.sub_group : ''}` : `CH ${a.ch} CODE ${a.code}`;
            
            let logType: 'error' | 'warn' | 'info' = 'info';
            let msg = `Event at ${a.distance}m. Temp: ${a.temp}°C`;
            
            if (a.alarm_type === 2) {
               logType = 'error';
               msg = `CRITICAL OVERHEAT DETECTED at ${a.distance}m! Temperature reached ${a.temp}°C`;
            } else if (a.alarm_type === 1) {
               logType = 'warn';
               msg = `Warning threshold exceeded at ${a.distance}m (${a.temp}°C)`;
            } else if (a.alarm_type === 4) {
               logType = 'error';
               msg = `FIBER BREAK DETECTED at ${a.distance}m!`;
            }

            return {
              id: `L-${a.id}`,
              type: logType,
              timestamp: new Date(a.time),
              segment: segmentName,
              msg: msg,
              user: 'DTS-UNIT'
            };
          });
          setHwLogs(mappedLogs);
        } else {
          // Fetch system logs
          const logs: SystemLog[] = await invoke('get_system_logs');
          if (!isMounted) return;
          // Filter by date if selected
          if (selectedDate) {
             setSysLogs(logs.filter(l => l.timestamp.startsWith(selectedDate)));
          } else {
             setSysLogs(logs);
          }
        }
        setLoading(false);
      } catch (err) {
        console.error(err);
        setLoading(false);
      }
    };
    
    fetchLogs();
    
    const timer = setInterval(fetchLogs, 10000);
    return () => { isMounted = false; clearInterval(timer); };
  }, [logMode, selectedDate]);

  const getLogIcon = (type: string) => {
    switch (type) {
      case 'info': return <Info size={16} className="text-blue-400" />;
      case 'warn': return <AlertTriangle size={16} className="text-yellow-500" />;
      case 'error': return <AlertCircle size={16} className="text-red-500" />;
      case 'CONFIG': return <Settings size={16} className="text-blue-400" />;
      case 'SYSTEM': return <Power size={16} className="text-purple-400" />;
      case 'ALARM': return <AlertTriangle size={16} className="text-yellow-500" />;
      case 'AUTH': return <LogIn size={16} className="text-green-400" />;
      default: return <Info size={16} className="text-text-secondary" />;
    }
  };

  const getLogBadge = (type: string) => {
    switch (type) {
      case 'info': return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-500/10 text-blue-400 border border-blue-500/30">INFO</span>;
      case 'warn': return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-yellow-500/10 text-yellow-500 border border-yellow-500/30">WARNING</span>;
      case 'error': return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-red-500/10 text-red-500 border border-red-500/30">ALARM</span>;
      case 'CONFIG': return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-500/10 text-blue-400 border border-blue-500/30">CONFIG</span>;
      case 'SYSTEM': return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-purple-500/10 text-purple-400 border border-purple-500/30">SYSTEM</span>;
      case 'ALARM': return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-yellow-500/10 text-yellow-500 border border-yellow-500/30">TRIGGER</span>;
      case 'AUTH': return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-green-500/10 text-green-400 border border-green-500/30">AUTH</span>;
      default: return null;
    }
  };

  return (
    <div className="h-screen w-full bg-bg-base flex flex-col font-sans overflow-hidden text-text-primary transition-colors duration-200">
      <TopNavbar 
        isDarkMode={isDarkMode} 
        setIsDarkMode={setIsDarkMode} 
        userRole={userRole}
        userId={userId}
        isFullscreen={false}
      />

      <div className="flex-1 flex flex-col p-4 md:p-6 space-y-4 overflow-y-auto">
        
        {/* HEADER */}
        <div className="flex flex-col md:flex-row md:items-center justify-between">
          <div className="flex items-center text-scada-primary mb-4 md:mb-0">
            <History size={28} className="mr-3" />
            <h1 className="text-2xl font-bold tracking-widest uppercase">EVENT LOGS</h1>
          </div>
          
          <div className="flex items-center space-x-3">
            <div className="flex bg-bg-surface p-1 rounded-lg border border-border mr-2">
              <button
                onClick={() => { setLogMode('hardware'); setFilterType('all'); }}
                className={`flex items-center px-4 py-2 font-mono text-sm font-bold transition-colors ${
                  logMode === 'hardware' ? 'bg-scada-primary/20 text-scada-primary border-b-2 border-scada-primary' : 'text-text-secondary hover:bg-bg-surface hover:text-text-primary border-b-2 border-transparent'
                }`}
              >
                <Server size={16} className="mr-2" /> HARDWARE LOGS (DTS)
              </button>
              <button
                onClick={() => { setLogMode('system'); setFilterType('all'); }}
                className={`flex items-center px-4 py-2 font-mono text-sm font-bold transition-colors ${
                  logMode === 'system' ? 'bg-scada-primary/20 text-scada-primary border-b-2 border-scada-primary' : 'text-text-secondary hover:bg-bg-surface hover:text-text-primary border-b-2 border-transparent'
                }`}
              >
                <Layout size={16} className="mr-2" /> SENTRY LOGS (SISTEM)
              </button>
            </div>
            
            <div className="flex bg-bg-panel border border-border rounded-lg overflow-hidden shadow-sm">
              <input type="date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)} className="bg-bg-panel px-4 py-2 text-sm text-text-primary outline-none" />
            </div>
            
            <button onClick={() => exportElementToPDF('logs-export-container', `DTS_Logs_${new Date().getTime()}`)} className="flex items-center px-4 py-2 bg-bg-panel border border-border rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-surface transition-colors font-bold text-sm shadow-sm">
              <Download size={16} className="mr-2" /> EXPORT
            </button>
          </div>
        </div>

        {/* FILTERS */}
        <div className="flex items-center justify-between bg-bg-panel border border-border rounded-xl p-4 shadow-sm">
          <div className="flex items-center flex-1 max-w-md bg-bg-base border border-border rounded-lg px-3 py-2 focus-within:border-scada-primary transition-colors">
            <Search size={16} className="text-text-secondary mr-2" />
            <input 
              type="text" 
              placeholder="Search messages or segments..." 
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="bg-transparent border-none outline-none text-sm text-text-primary w-full"
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold text-text-secondary uppercase tracking-widest mr-2">Filter:</span>
            
            <button onClick={() => setFilterType('all')} className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-colors ${filterType === 'all' ? 'bg-bg-surface text-text-primary border border-border' : 'text-text-secondary hover:bg-bg-base'}`}>All</button>
            
            {logMode === 'hardware' ? (
              <>
                <button onClick={() => setFilterType('info')} className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-colors ${filterType === 'info' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' : 'text-text-secondary hover:bg-bg-base'}`}>Info</button>
                <button onClick={() => setFilterType('warn')} className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-colors ${filterType === 'warn' ? 'bg-yellow-500/20 text-yellow-500 border border-yellow-500/30' : 'text-text-secondary hover:bg-bg-base'}`}>Warning</button>
                <button onClick={() => setFilterType('error')} className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-colors ${filterType === 'error' ? 'bg-red-500/20 text-red-500 border border-red-500/30' : 'text-text-secondary hover:bg-bg-base'}`}>Alarm</button>
              </>
            ) : (
              <>
                <button onClick={() => setFilterType('CONFIG')} className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-colors ${filterType === 'CONFIG' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' : 'text-text-secondary hover:bg-bg-base'}`}>Config</button>
                <button onClick={() => setFilterType('SYSTEM')} className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-colors ${filterType === 'SYSTEM' ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30' : 'text-text-secondary hover:bg-bg-base'}`}>System</button>
                <button onClick={() => setFilterType('ALARM')} className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-colors ${filterType === 'ALARM' ? 'bg-yellow-500/20 text-yellow-500 border border-yellow-500/30' : 'text-text-secondary hover:bg-bg-base'}`}>Trigger</button>
                <button onClick={() => setFilterType('AUTH')} className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase transition-colors ${filterType === 'AUTH' ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'text-text-secondary hover:bg-bg-base'}`}>Auth</button>
              </>
            )}
          </div>
        </div>

        {/* LOGS TABLE */}
        <div id="logs-export-container" className="flex-1 bg-bg-panel border border-border rounded-xl shadow-sm overflow-hidden flex flex-col relative">
          <div className="grid grid-cols-12 gap-4 p-4 border-b border-border bg-bg-surface font-bold text-xs text-text-secondary uppercase tracking-wider">
            <div className="col-span-2">TIMESTAMP</div>
            <div className="col-span-2">{logMode === 'hardware' ? 'SEGMENT' : 'EVENT TYPE'}</div>
            <div className="col-span-1">STATUS</div>
            <div className="col-span-5">MESSAGE</div>
            <div className="col-span-2 text-right">SOURCE</div>
          </div>
          
          <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
            {loading ? (
               <div className="flex items-center justify-center h-40">
                 <p className="text-text-secondary animate-pulse font-mono">LOADING LOGS...</p>
               </div>
            ) : logMode === 'hardware' ? (
              hwLogs.filter(log => {
                const matchesSearch = log.msg.toLowerCase().includes(searchTerm.toLowerCase()) || log.segment.toLowerCase().includes(searchTerm.toLowerCase());
                const matchesType = filterType === 'all' || log.type === filterType;
                return matchesSearch && matchesType;
              }).length === 0 ? (
                <div className="flex flex-col items-center justify-center h-40 text-text-secondary">
                  <FileText size={32} className="mb-2 opacity-50" />
                  <p className="text-sm font-mono">No hardware logs found for selected filters.</p>
                </div>
              ) : (
                hwLogs.filter(log => {
                  const matchesSearch = log.msg.toLowerCase().includes(searchTerm.toLowerCase()) || log.segment.toLowerCase().includes(searchTerm.toLowerCase());
                  const matchesType = filterType === 'all' || log.type === filterType;
                  return matchesSearch && matchesType;
                }).map((log, index) => (
                  <div key={log.id + index} className="grid grid-cols-12 gap-4 p-3 hover:bg-bg-surface border-b border-border/50 items-center transition-colors group">
                    <div className="col-span-2 text-sm font-mono text-text-secondary">{log.timestamp.toLocaleString()}</div>
                    <div className="col-span-2 text-sm font-bold text-text-primary truncate" title={log.segment}>{log.segment}</div>
                    <div className="col-span-1 flex items-center space-x-2">
                      {getLogIcon(log.type)}
                      {getLogBadge(log.type)}
                    </div>
                    <div className="col-span-5 text-sm text-text-primary pr-4">{log.msg}</div>
                    <div className="col-span-2 text-right">
                      <span className="inline-block px-2 py-1 bg-bg-base rounded text-xs font-mono text-text-secondary border border-border group-hover:border-scada-primary/30 transition-colors">
                        {log.user}
                      </span>
                    </div>
                  </div>
                ))
              )
            ) : (
              sysLogs.filter(log => {
                const matchesSearch = log.message.toLowerCase().includes(searchTerm.toLowerCase());
                const matchesType = filterType === 'all' || log.event_type === filterType;
                return matchesSearch && matchesType;
              }).length === 0 ? (
                <div className="flex flex-col items-center justify-center h-40 text-text-secondary">
                  <FileText size={32} className="mb-2 opacity-50" />
                  <p className="text-sm font-mono">No system logs found for selected filters.</p>
                </div>
              ) : (
                sysLogs.filter(log => {
                  const matchesSearch = log.message.toLowerCase().includes(searchTerm.toLowerCase());
                  const matchesType = filterType === 'all' || log.event_type === filterType;
                  return matchesSearch && matchesType;
                }).map((log, index) => (
                  <div key={log.id + index} className="grid grid-cols-12 gap-4 p-3 hover:bg-bg-surface border-b border-border/50 items-center transition-colors group">
                    <div className="col-span-2 text-sm font-mono text-text-secondary">{log.timestamp}</div>
                    <div className="col-span-2 text-sm font-bold text-text-primary truncate">{log.event_type}</div>
                    <div className="col-span-1 flex items-center space-x-2">
                      {getLogIcon(log.event_type)}
                      {getLogBadge(log.event_type)}
                    </div>
                    <div className="col-span-5 text-sm text-text-primary pr-4">{log.message}</div>
                    <div className="col-span-2 text-right">
                      <span className="inline-block px-2 py-1 bg-scada-primary/10 rounded text-xs font-mono text-scada-primary border border-scada-primary/30 transition-colors">
                        SENTRY CORE
                      </span>
                    </div>
                  </div>
                ))
              )
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
"""

with open('src/pages/LogsPage.tsx', 'w') as f:
    f.write(new_logs)

