import re

with open('src/pages/LogsPage.tsx', 'r') as f:
    content = f.read()

# I will rewrite LogsPage completely to combine Hardware and System logs into a single array
new_logs_page = """import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { exportElementToPDF } from '../utils/exportPdf';
import { History, Download, AlertTriangle, Info, AlertCircle, Search, FileText, Settings, Power, LogIn } from 'lucide-react';
import TopNavbar from '../components/layout/TopNavbar';

interface CombinedLog {
  id: string;
  type: 'info' | 'warn' | 'error' | 'CONFIG' | 'SYSTEM' | 'ALARM' | 'AUTH';
  timestamp: Date;
  segment: string;
  msg: string;
  source: 'DTS-UNIT' | 'SENTRY CORE';
}

export default function LogsPage() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true;
  });
  const [userRole, setUserRole] = useState('OPERATOR');
  const [userId, setUserId] = useState('OP-7729');
  
  const [logs, setLogs] = useState<CombinedLog[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'info' | 'warn' | 'error' | 'CONFIG' | 'SYSTEM' | 'ALARM' | 'AUTH'>('all');
  const [filterSource, setFilterSource] = useState<'all' | 'DTS-UNIT' | 'SENTRY CORE'>('all');

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
        const dateParam = selectedDate ? selectedDate : null;
        
        // Fetch both hardware and system logs
        const [alarms, mappings, sysLogsData] = await Promise.all([
          invoke<any[]>('get_alarms', { date: dateParam }),
          invoke<any[]>('get_segment_mappings'),
          invoke<any[]>('get_system_logs')
        ]);
        
        if (!isMounted) return;

        const hwLogs: CombinedLog[] = alarms.map((a: any) => {
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
            id: `HW-${a.id}`,
            type: logType,
            timestamp: new Date(a.time),
            segment: segmentName,
            msg: msg,
            source: 'DTS-UNIT'
          };
        });
        
        const sysLogs: CombinedLog[] = sysLogsData
          .filter(l => !selectedDate || l.timestamp.startsWith(selectedDate))
          .map((l: any) => ({
            id: `SYS-${l.id}`,
            type: l.event_type as any,
            timestamp: new Date(l.timestamp),
            segment: l.event_type,
            msg: l.message,
            source: 'SENTRY CORE'
          }));
          
        const combined = [...hwLogs, ...sysLogs].sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
        setLogs(combined);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setLoading(false);
      }
    };
    
    fetchLogs();
    
    const timer = setInterval(fetchLogs, 10000);
    return () => { isMounted = false; clearInterval(timer); };
  }, [selectedDate]);

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
      default: return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-gray-500/10 text-gray-400 border border-gray-500/30">{type}</span>;
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
            <div className="flex bg-bg-panel border border-border rounded-lg overflow-hidden shadow-sm">
              <input type="date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)} className="bg-bg-panel px-4 py-2 text-sm text-text-primary outline-none" />
            </div>
            
            <button onClick={() => exportElementToPDF('logs-export-container', `DTS_Logs_${new Date().getTime()}`)} className="flex items-center px-4 py-2 bg-bg-panel border border-border rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-surface transition-colors font-bold text-sm shadow-sm">
              <Download size={16} className="mr-2" /> EXPORT
            </button>
          </div>
        </div>

        {/* FILTERS */}
        <div className="flex flex-wrap items-center justify-between bg-bg-panel border border-border rounded-xl p-4 shadow-sm gap-4">
          <div className="flex items-center flex-1 min-w-[300px] bg-bg-base border border-border rounded-lg px-3 py-2 focus-within:border-scada-primary transition-colors">
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
            <span className="text-xs font-bold text-text-secondary uppercase tracking-widest mr-2">Source:</span>
            <select 
              value={filterSource} 
              onChange={e => setFilterSource(e.target.value as any)}
              className="bg-bg-base border border-border rounded-lg px-3 py-1.5 text-sm text-text-primary outline-none"
            >
              <option value="all">All Sources</option>
              <option value="DTS-UNIT">Hardware (DTS)</option>
              <option value="SENTRY CORE">System (Sentry)</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold text-text-secondary uppercase tracking-widest mr-2">Filter:</span>
            <select 
              value={filterType} 
              onChange={e => setFilterType(e.target.value as any)}
              className="bg-bg-base border border-border rounded-lg px-3 py-1.5 text-sm text-text-primary outline-none"
            >
              <option value="all">All Types</option>
              <option value="info">Info</option>
              <option value="warn">Warning</option>
              <option value="error">Alarm (Error)</option>
              <option value="CONFIG">Config</option>
              <option value="SYSTEM">System</option>
              <option value="ALARM">Trigger</option>
              <option value="AUTH">Auth</option>
            </select>
          </div>
        </div>

        {/* LOGS TABLE */}
        <div id="logs-export-container" className="flex-1 bg-bg-panel border border-border rounded-xl shadow-sm overflow-hidden flex flex-col relative">
          <div className="grid grid-cols-12 gap-4 p-4 border-b border-border bg-bg-surface font-bold text-xs text-text-secondary uppercase tracking-wider">
            <div className="col-span-2">TIMESTAMP</div>
            <div className="col-span-2">SEGMENT / EVENT</div>
            <div className="col-span-1">STATUS</div>
            <div className="col-span-5">MESSAGE</div>
            <div className="col-span-2 text-right">SOURCE</div>
          </div>
          
          <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
            {loading && logs.length === 0 ? (
               <div className="flex items-center justify-center h-40">
                 <p className="text-text-secondary animate-pulse font-mono">LOADING LOGS...</p>
               </div>
            ) : (
              logs.filter(log => {
                const matchesSearch = log.msg.toLowerCase().includes(searchTerm.toLowerCase()) || log.segment.toLowerCase().includes(searchTerm.toLowerCase());
                const matchesType = filterType === 'all' || log.type === filterType;
                const matchesSource = filterSource === 'all' || log.source === filterSource;
                return matchesSearch && matchesType && matchesSource;
              }).length === 0 ? (
                <div className="flex flex-col items-center justify-center h-40 text-text-secondary">
                  <FileText size={32} className="mb-2 opacity-50" />
                  <p className="text-sm font-mono">No logs found for selected filters.</p>
                </div>
              ) : (
                logs.filter(log => {
                  const matchesSearch = log.msg.toLowerCase().includes(searchTerm.toLowerCase()) || log.segment.toLowerCase().includes(searchTerm.toLowerCase());
                  const matchesType = filterType === 'all' || log.type === filterType;
                  const matchesSource = filterSource === 'all' || log.source === filterSource;
                  return matchesSearch && matchesType && matchesSource;
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
                      <span className={`inline-block px-2 py-1 rounded text-[10px] font-bold uppercase transition-colors ${
                        log.source === 'DTS-UNIT' 
                        ? 'bg-bg-base text-text-secondary border border-border group-hover:border-scada-primary/30' 
                        : 'bg-scada-primary/10 text-scada-primary border border-scada-primary/30'
                      }`}>
                        {log.source}
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
    f.write(new_logs_page)

