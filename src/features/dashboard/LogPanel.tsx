import { History, Wifi, Clock } from 'lucide-react';

export interface LogData {
  id: number;
  time: string;
  msg: string;
  type: string;
}

interface LogPanelProps {
  isFullscreen: boolean;
  dummyLogs: LogData[];
  currentTime: Date;
}

export default function LogPanel({ isFullscreen, dummyLogs, currentTime }: LogPanelProps) {
  return (
    <div className={`absolute bottom-4 right-4 z-30 flex flex-col space-y-4 ${isFullscreen ? 'w-72' : 'w-96'} pointer-events-none transition-all duration-500`}>
      {/* SYSTEM LOGS */}
      <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl p-4 shadow-lg pointer-events-auto flex flex-col transition-all duration-500">
        <div className="text-sm font-bold text-text-primary uppercase tracking-widest flex items-center border-b border-border pb-2 mb-3 shrink-0">
          <History size={16} className="mr-2 text-scada-primary" /> SYSTEM LOGS
        </div>
        <div className={`flex flex-col space-y-2 overflow-y-auto custom-scrollbar pr-1 transition-all duration-500 ${isFullscreen ? 'max-h-[120px]' : 'max-h-[200px]'}`}>
          {dummyLogs.map(log => (
            <div key={log.id} className="flex flex-col bg-bg-surface p-2.5 rounded-lg border border-border shadow-sm shrink-0">
              <div className="flex justify-between items-center mb-1.5">
                <span className="text-[10px] font-mono text-text-secondary bg-bg-base px-1.5 py-0.5 rounded border border-border">{log.time}</span>
                <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${log.type === 'error' ? 'bg-red-500/20 text-red-400' : log.type === 'warn' ? 'bg-yellow-500/20 text-yellow-500' : 'bg-scada-primary/20 text-scada-primary'}`}>
                  {log.type}
                </span>
              </div>
              <p className="text-xs text-text-primary line-clamp-2 leading-relaxed">{log.msg}</p>
            </div>
          ))}
        </div>
      </div>

      {/* SYSTEM STATUS & TIME */}
      <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl shadow-lg p-3 pointer-events-auto transition-all duration-300 flex items-center justify-between">
        <div className="flex flex-col items-start pl-2">
          <span className="text-[10px] text-text-secondary uppercase font-bold tracking-widest">DTS Connection</span>
          <div className="flex items-center text-scada-success font-bold text-xs mt-1">
            <Wifi size={14} className="mr-1 animate-pulse" />
            ONLINE (MySQL)
          </div>
        </div>
        
        <div className="h-8 w-px bg-border"></div>
        
        <div className="flex flex-col items-end min-w-[120px] pr-2">
          <span className="text-[10px] font-bold text-text-secondary font-mono tracking-widest uppercase">
            {currentTime.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })}
          </span>
          <div className="flex items-center text-scada-primary font-mono font-bold text-base mt-0.5">
            <Clock size={14} className="mr-1.5" />
            {currentTime.toLocaleTimeString('en-GB', { hour12: false })}
          </div>
        </div>
      </div>
    </div>
  );
}
