import { useState, useEffect } from 'react';
import { History, Calendar, Download, AlertTriangle, Info, AlertCircle, Search, FileText } from 'lucide-react';
import TopNavbar from '../components/layout/TopNavbar';
import { DUMMY_AREAS } from '../data/constants';

// Generate complex dummy logs
const generateDummyLogs = () => {
  const logs = [];
  const now = new Date();
  
  for (let i = 0; i < 50; i++) {
    const time = new Date(now.getTime() - Math.random() * 7 * 24 * 60 * 60 * 1000); // Random within last 7 days
    
    const types = ['info', 'warn', 'error'];
    const type = types[Math.floor(Math.random() * types.length)] as 'info' | 'warn' | 'error';
    
    let msg = '';
    let segment = '-';
    
    if (type === 'info') {
      const msgs = ['System heartbeat OK', 'User Operator logged in', 'Routine calibration completed', 'Data synced with central server'];
      msg = msgs[Math.floor(Math.random() * msgs.length)];
    } else {
      const area = DUMMY_AREAS[Math.floor(Math.random() * DUMMY_AREAS.length)];
      segment = area.name;
      
      if (type === 'warn') {
        msg = `Temperature warning threshold exceeded: ${(Math.random() * 5 + 60).toFixed(1)}°C`;
      } else {
        msg = `ALARM TRIGGERED: CRITICAL TEMP DETECTED AT ${(Math.random() * 10 + 75).toFixed(1)}°C`;
      }
    }
    
    logs.push({
      id: 5000 + i,
      timestamp: time,
      type,
      msg,
      segment
    });
  }
  
  // Sort descending by time
  return logs.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
};

const DUMMY_HISTORY_LOGS = generateDummyLogs();

export default function LogsPage() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true;
  });
  const [userRole, setUserRole] = useState('OPERATOR');
  const [userId, setUserId] = useState('OP-7729');
  
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'info' | 'warn' | 'error'>('all');

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

  const filteredLogs = DUMMY_HISTORY_LOGS.filter(log => {
    const matchesSearch = log.msg.toLowerCase().includes(searchTerm.toLowerCase()) || log.segment.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'all' || log.type === filterType;
    return matchesSearch && matchesType;
  });

  const getLogIcon = (type: string) => {
    switch (type) {
      case 'info': return <Info size={16} className="text-blue-400" />;
      case 'warn': return <AlertTriangle size={16} className="text-yellow-500" />;
      case 'error': return <AlertCircle size={16} className="text-red-500" />;
      default: return <Info size={16} className="text-text-secondary" />;
    }
  };

  const getLogBadge = (type: string) => {
    switch (type) {
      case 'info': return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-500/10 text-blue-400 border border-blue-500/30">INFO</span>;
      case 'warn': return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-yellow-500/10 text-yellow-500 border border-yellow-500/30">WARNING</span>;
      case 'error': return <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-red-500/10 text-red-500 border border-red-500/30">ALARM</span>;
      default: return null;
    }
  };

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
        {/* HEADER */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center space-y-4 md:space-y-0">
          <div>
            <h2 className="text-2xl font-bold tracking-widest text-text-primary flex items-center">
              <History className="mr-3 text-scada-primary" size={28} /> 
              SYSTEM ALARM & LOG HISTORY
            </h2>
            <p className="text-text-secondary font-mono mt-1">Review historical system events, warnings, and critical alarms.</p>
          </div>

          <div className="flex space-x-3">
            <button className="flex items-center px-4 py-2 bg-bg-panel border border-border rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-surface transition-colors font-bold text-sm shadow-sm">
              <Calendar size={16} className="mr-2" /> SELECT DATE RANGE
            </button>
            <button className="flex items-center px-4 py-2 bg-bg-panel border border-border rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-surface transition-colors font-bold text-sm shadow-sm">
              <Download size={16} className="mr-2" /> EXPORT PDF/CSV
            </button>
          </div>
        </div>

        {/* CONTROLS */}
        <div className="flex flex-col md:flex-row justify-between items-center bg-bg-panel border border-border rounded-xl p-4 shadow-sm shrink-0">
          <div className="flex space-x-2">
            <button 
              onClick={() => setFilterType('all')}
              className={`px-4 py-2 text-xs font-bold rounded-md transition-colors ${filterType === 'all' ? 'bg-bg-surface text-text-primary border border-border' : 'text-text-secondary hover:bg-bg-surface/50 border border-transparent'}`}
            >
              ALL LOGS
            </button>
            <button 
              onClick={() => setFilterType('error')}
              className={`px-4 py-2 text-xs font-bold rounded-md flex items-center transition-colors ${filterType === 'error' ? 'bg-red-500/10 text-red-400 border border-red-500/30' : 'text-text-secondary hover:bg-red-500/5 hover:text-red-400 border border-transparent'}`}
            >
              <AlertCircle size={14} className="mr-1" /> ALARMS
            </button>
            <button 
              onClick={() => setFilterType('warn')}
              className={`px-4 py-2 text-xs font-bold rounded-md flex items-center transition-colors ${filterType === 'warn' ? 'bg-yellow-500/10 text-yellow-500 border border-yellow-500/30' : 'text-text-secondary hover:bg-yellow-500/5 hover:text-yellow-500 border border-transparent'}`}
            >
              <AlertTriangle size={14} className="mr-1" /> WARNINGS
            </button>
            <button 
              onClick={() => setFilterType('info')}
              className={`px-4 py-2 text-xs font-bold rounded-md flex items-center transition-colors ${filterType === 'info' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'text-text-secondary hover:bg-blue-500/5 hover:text-blue-400 border border-transparent'}`}
            >
              <Info size={14} className="mr-1" /> INFO
            </button>
          </div>

          <div className="relative w-full max-w-xs mt-4 md:mt-0">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-secondary" size={16} />
            <input 
              type="text" 
              placeholder="Search logs or segments..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-bg-surface border border-border rounded-lg py-2 pl-9 pr-4 text-sm text-text-primary focus:outline-none focus:border-scada-primary focus:ring-1 focus:ring-scada-primary/50 transition-all font-mono"
            />
          </div>
        </div>

        {/* LOGS TABLE */}
        <div className="bg-bg-panel border border-border rounded-xl flex-1 flex flex-col shadow-lg overflow-hidden">
          <div className="overflow-x-auto flex-1 custom-scrollbar">
            <table className="w-full text-left border-collapse">
              <thead className="bg-bg-surface sticky top-0 z-10 shadow-sm border-b border-border">
                <tr>
                  <th className="py-3 px-6 text-text-secondary font-bold uppercase text-xs tracking-wider w-12 text-center">Type</th>
                  <th className="py-3 px-6 text-text-secondary font-bold uppercase text-xs tracking-wider">Date / Time</th>
                  <th className="py-3 px-6 text-text-secondary font-bold uppercase text-xs tracking-wider">Segment</th>
                  <th className="py-3 px-6 text-text-secondary font-bold uppercase text-xs tracking-wider w-1/2">Event Message</th>
                  <th className="py-3 px-6 text-text-secondary font-bold uppercase text-xs tracking-wider text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {filteredLogs.length > 0 ? filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-bg-surface/50 transition-colors group">
                    <td className="py-3 px-6 text-center">
                      <div className="flex justify-center">{getLogIcon(log.type)}</div>
                    </td>
                    <td className="py-3 px-6 font-mono text-sm text-text-secondary group-hover:text-text-primary transition-colors">
                      <div>{log.timestamp.toLocaleDateString()}</div>
                      <div className="text-xs opacity-70">{log.timestamp.toLocaleTimeString()}</div>
                    </td>
                    <td className="py-3 px-6">
                      <span className="font-bold text-sm">{log.segment}</span>
                    </td>
                    <td className="py-3 px-6">
                      <div className="flex items-center space-x-2">
                        {getLogBadge(log.type)}
                        <span className={`font-mono text-sm ${log.type === 'error' ? 'text-red-400 font-bold' : log.type === 'warn' ? 'text-yellow-500' : 'text-text-secondary'}`}>
                          {log.msg}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-6 text-right">
                      <button className="p-1.5 rounded-md text-text-secondary hover:text-scada-primary hover:bg-scada-primary/10 transition-colors" title="View Details">
                        <FileText size={16} />
                      </button>
                    </td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan={5} className="py-12 text-center text-text-secondary font-mono">
                      No logs found matching your filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          
          <div className="bg-bg-surface p-3 border-t border-border flex justify-between items-center text-xs text-text-secondary font-mono">
            <span>Showing {filteredLogs.length} of {DUMMY_HISTORY_LOGS.length} records</span>
            <div className="flex space-x-1">
              <button className="px-2 py-1 rounded hover:bg-bg-panel border border-transparent hover:border-border text-text-secondary">Prev</button>
              <button className="px-2 py-1 rounded bg-bg-panel border border-border text-text-primary">1</button>
              <button className="px-2 py-1 rounded hover:bg-bg-panel border border-transparent hover:border-border text-text-secondary">2</button>
              <button className="px-2 py-1 rounded hover:bg-bg-panel border border-transparent hover:border-border text-text-secondary">3</button>
              <button className="px-2 py-1 rounded hover:bg-bg-panel border border-transparent hover:border-border text-text-secondary">Next</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
