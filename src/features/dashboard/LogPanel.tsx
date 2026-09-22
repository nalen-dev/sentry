// @ts-nocheck
import { History, Wifi, Clock, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

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
  const navigate = useNavigate();

  return (
    <div className={`absolute bottom-4 right-4 z-30 flex flex-col space-y-4 ${isFullscreen ? 'w-72' : 'w-96'} pointer-events-none transition-all duration-500`}>
      {/* SYSTEM LOGS */}
      <div 
        onClick={() => navigate('/logs')}
        className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl p-4 shadow-lg pointer-events-auto flex flex-col transition-all duration-500 cursor-pointer hover:border-scada-primary/50 group"
      >
        <div className="text-sm font-bold text-text-primary uppercase tracking-widest flex items-center justify-between border-b border-border pb-2 mb-3 shrink-0">
          <div className="flex items-center">
            <History size={16} className="mr-2 text-scada-primary group-hover:scale-110 transition-transform" /> SYSTEM LOGS
          </div>
          <ArrowRight size={14} className="text-scada-primary opacity-0 group-hover:opacity-100 transition-opacity" />
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

      {/* LOGOS */}
      <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl shadow-lg p-3 pointer-events-auto transition-all duration-300 flex items-center justify-center space-x-4">
        <div className="bg-white rounded-md px-3 py-1.5 flex items-center justify-center h-12 shadow-sm">
          <img src="/logo-itm.png" alt="ITM Logo" className="h-full w-auto object-contain" />
        </div>
        <div className="h-8 w-px bg-border"></div>
        <div className="bg-white rounded-md px-3 py-1.5 flex items-center justify-center h-12 shadow-sm">
          <img src="/logo-kag.jpeg" alt="KAG Logo" className="h-full w-auto object-contain" />
        </div>
      </div>
    </div>
  );
}
