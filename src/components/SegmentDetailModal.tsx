import { useState, useEffect } from 'react';
import { X, Save, Activity, MapPin, AlignLeft, Info, Thermometer, AlertTriangle, Check, Edit2 } from 'lucide-react';
import { LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';

export interface SegmentData {
  id: number;
  name: string;
  original_name?: string;
  status: string;
  temp: number;
  distance: string;
  isAlarm: boolean;
  group?: string;
  areaLocation?: string;
  photoUrl?: string;
  temp_avg?: number;
  temp_min?: number;
  temp_max?: number;
  temp_min_p?: number;
  temp_max_p?: number;
  notes?: string;
  dts_ch?: number;
  dts_code?: number;
  start_m?: number;
  end_m?: number;
}

interface SegmentDetailModalProps {
  segment: SegmentData;
  onClose: () => void;
  isAdmin: boolean;
  onRename?: (id: number, newName: string) => void;
}

export default function SegmentDetailModal({ segment, onClose, isAdmin, onRename }: SegmentDetailModalProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState(segment.name);
  const [notes, setNotes] = useState('');

  const [chartMode, setChartMode] = useState<'history' | 'distance'>('history');
  const [chartData, setChartData] = useState<any[]>([]);

  const handleSaveRename = () => {
    if (onRename && editName.trim() !== '') {
      onRename(segment.id, editName);
    }
    setIsEditing(false);
  };

  const relatedLogs = [
    { id: 1, time: '14:22:00', msg: 'System check normal', type: 'info' },
    { id: 2, time: '12:05:11', msg: 'Slight temp increase detected', type: 'warn' },
    { id: 3, time: '09:00:00', msg: 'Daily reset initiated', type: 'info' },
  ];

  useEffect(() => {
    let isMounted = true;
    import('@tauri-apps/api/core').then(({ invoke }) => {
      const fetchData = async () => {
        if (!segment.dts_ch || !segment.dts_code) return;
        try {
          if (chartMode === 'history') {
            const data = await invoke<any[]>('get_segment_history', { dtsCh: segment.dts_ch, dtsCode: segment.dts_code, minutes: 30 });
            if (isMounted) setChartData(data);
          } else {
            // Distance curve
            const startM = segment.start_m || 0;
            const endM = segment.end_m || 1000;
            const data = await invoke<any[]>('get_segment_curve', { dtsCh: segment.dts_ch, startM, endM });
            if (isMounted) setChartData(data);
          }
        } catch (err) {
          console.error("Failed to fetch chart data", err);
        }
      };

      fetchData();
      const timer = setInterval(fetchData, 5000);
      return () => { isMounted = false; clearInterval(timer); };
    });
  }, [chartMode, segment.dts_ch, segment.dts_code, segment.start_m, segment.end_m]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-bg-panel/80 backdrop-blur-sm" onClick={onClose}></div>
      
      {/* Modal Container */}
      <div className="relative w-full max-w-5xl h-[80vh] bg-bg-surface border border-border rounded-2xl shadow-2xl flex flex-col animate-in zoom-in-95 duration-200">
        
        {/* HEADER */}
        <div className="flex justify-between items-start p-6 border-b border-border bg-bg-panel rounded-t-2xl">
          <div className="flex items-start space-x-4">
            <div className={`p-3 rounded-xl mt-1 ${segment.isAlarm ? 'bg-red-500/20 text-red-500 shadow-[0_0_15px_rgba(239,68,68,0.5)]' : 'bg-scada-primary/20 text-scada-primary'}`}>
              <AlertTriangle size={28} />
            </div>
            <div>
              {isEditing ? (
                <div className="flex items-center space-x-2">
                  <input 
                    type="text" 
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    className="bg-bg-base border border-scada-primary rounded-lg px-3 py-1.5 text-2xl font-bold text-text-primary focus:outline-none w-64"
                    autoFocus
                  />
                  <button onClick={handleSaveRename} className="p-2 text-scada-success hover:bg-bg-base rounded-lg"><Check size={20} /></button>
                  <button onClick={() => setIsEditing(false)} className="p-2 text-red-400 hover:bg-bg-base rounded-lg"><X size={20} /></button>
                </div>
              ) : (
                <h2 className="text-3xl font-bold text-text-primary flex items-center group">
                  {segment.name}
                  {isAdmin && (
                    <button 
                      onClick={() => setIsEditing(true)}
                      className="ml-3 p-1.5 text-text-secondary opacity-0 group-hover:opacity-100 hover:text-scada-primary hover:bg-bg-base rounded-md transition-all"
                    >
                      <Edit2 size={16} />
                    </button>
                  )}
                </h2>
              )}
              <p className="text-sm text-text-secondary font-mono tracking-widest uppercase mt-1">
                AreaTable (DTS): <span className="text-text-primary font-bold">{segment.original_name || 'N/A'}</span> • ID: {segment.id}
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 text-text-secondary hover:text-text-primary hover:bg-bg-base rounded-lg transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* BODY */}
        <div className="flex-1 flex overflow-hidden">
          
          {/* LEFT COLUMN: INFO & PHOTO & NOTES */}
          <div className="w-1/3 flex flex-col border-r border-border bg-bg-base overflow-y-auto custom-scrollbar">
            
            {/* Stats Overview */}
            <div className="p-6 border-b border-border space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-text-secondary uppercase tracking-widest flex items-center"><MapPin size={14} className="mr-2" /> Distance</span>
                <span className="font-mono text-text-primary">{segment.distance}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-text-secondary uppercase tracking-widest flex items-center"><AlignLeft size={14} className="mr-2" /> Group</span>
                <span className="font-mono text-text-primary">{segment.group || 'BC MAIN - 01'}</span>
              </div>
              
              <div className="pt-4 border-t border-border/50 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-text-secondary uppercase tracking-widest flex items-center"><Thermometer size={14} className="mr-2" /> Max Temp</span>
                  <div className="text-right">
                    <span className="text-red-400 font-mono font-bold">{segment.temp_max ?? '-'}°C</span>
                    <p className="text-[10px] text-text-secondary font-mono">at {segment.temp_max_p ?? '-'}m</p>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-text-secondary uppercase tracking-widest flex items-center"><Thermometer size={14} className="mr-2" /> Min Temp</span>
                  <div className="text-right">
                    <span className="text-blue-400 font-mono font-bold">{segment.temp_min ?? '-'}°C</span>
                    <p className="text-[10px] text-text-secondary font-mono">at {segment.temp_min_p ?? '-'}m</p>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-text-secondary uppercase tracking-widest flex items-center"><Thermometer size={14} className="mr-2" /> Avg Temp</span>
                  <span className="text-scada-primary font-mono font-bold text-lg">{segment.temp_avg ?? segment.temp}°C</span>
                </div>
              </div>
            </div>



            {/* Admin Notes */}
            <div className="p-6 flex-1 flex flex-col min-h-[200px]">
              <span className="text-xs font-bold text-text-secondary uppercase tracking-widest mb-3 flex items-center"><Info size={14} className="mr-2" /> Admin Notes</span>
              {isAdmin ? (
                <div className="flex flex-col flex-1 h-full">
                  <textarea 
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    className="w-full flex-1 bg-bg-surface border border-border rounded-lg p-3 text-sm text-text-primary focus:outline-none focus:border-scada-primary transition-colors resize-none mb-3"
                    placeholder="Add operational notes for this segment..."
                  />
                  <button className="w-full bg-scada-primary/20 hover:bg-scada-primary text-scada-primary hover:text-white border border-scada-primary/50 transition-colors py-2 rounded-lg text-sm font-bold flex items-center justify-center">
                    <Save size={16} className="mr-2" /> SAVE NOTES
                  </button>
                </div>
              ) : (
                <div className="w-full flex-1 bg-bg-surface border border-border rounded-lg p-3 text-sm text-text-secondary">
                  {notes || 'No notes provided by Administrator.'}
                </div>
              )}
            </div>
            
          </div>

          {/* RIGHT COLUMN: CHART & LOGS */}
          <div className="w-2/3 flex flex-col p-6 space-y-6">
            
            {/* Chart */}
            <div className="h-1/2 flex flex-col bg-bg-base border border-border rounded-xl p-5 shadow-inner">
              <div className="flex justify-between items-center mb-4">
                <span className="text-xs font-bold text-text-primary uppercase tracking-widest flex items-center"><Activity size={16} className="mr-2 text-scada-primary" /> {chartMode === 'history' ? 'Temperature vs Time (History)' : 'Temperature vs Distance (Live)'}</span>
                <div className="flex bg-bg-panel p-1 rounded-md">
                  <button onClick={() => setChartMode('history')} className={`text-[10px] px-2 py-1 rounded transition-colors ${chartMode === 'history' ? 'bg-bg-surface text-scada-primary' : 'text-text-secondary hover:text-text-primary'}`}>TIME</button>
                  <button onClick={() => setChartMode('distance')} className={`text-[10px] px-2 py-1 rounded transition-colors ${chartMode === 'distance' ? 'bg-bg-surface text-scada-primary' : 'text-text-secondary hover:text-text-primary'}`}>DISTANCE</button>
                </div>
              </div>
              
              <div className="flex-1 w-full min-h-0">
                 <ResponsiveContainer width="100%" height="100%">
                   <RechartsLineChart data={chartData} margin={{ top: 5, right: 20, left: -20, bottom: 0 }}>
                     <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" opacity={0.3} />
                     <XAxis dataKey={chartMode === 'history' ? 'time' : 'distance'} stroke="#9ca3af" fontSize={12} tickMargin={10} />
                     <YAxis stroke="#9ca3af" fontSize={12} domain={[0, 100]} />
                     <RechartsTooltip 
                       contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', fontSize: '12px' }}
                       itemStyle={{ color: 'var(--scada-primary)' }}
                     />
                     <Line type="monotone" dataKey="temp" stroke="var(--scada-primary)" strokeWidth={2} dot={false} activeDot={{ r: 6, fill: 'var(--scada-primary)' }} connectNulls={true} />
                   </RechartsLineChart>
                 </ResponsiveContainer>
              </div>
            </div>

            {/* Related Logs */}
            <div className="flex-1 flex flex-col bg-bg-base border border-border rounded-xl p-5 shadow-inner min-h-0">
              <span className="text-xs font-bold text-text-primary uppercase tracking-widest mb-4 flex items-center"><AlignLeft size={16} className="mr-2 text-scada-primary" /> Related Logs</span>
              <div className="flex-1 overflow-y-auto custom-scrollbar space-y-2 pr-2">
                {relatedLogs.map(log => (
                  <div key={log.id} className="flex items-center justify-between bg-bg-surface p-3 rounded-lg border border-border shadow-sm">
                    <div className="flex items-center space-x-3">
                      <span className="text-xs font-mono text-text-secondary bg-bg-panel px-2 py-1 rounded border border-border">{log.time}</span>
                      <p className="text-sm text-text-primary">{log.msg}</p>
                    </div>
                    <span className={`text-[10px] px-2 py-1 rounded font-bold uppercase tracking-wider ${log.type === 'error' ? 'bg-red-500/20 text-red-400' : log.type === 'warn' ? 'bg-yellow-500/20 text-yellow-500' : 'bg-scada-primary/20 text-scada-primary'}`}>
                      {log.type}
                    </span>
                  </div>
                ))}
              </div>
            </div>

          </div>

        </div>
      </div>
    </div>
  );
}
