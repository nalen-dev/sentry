import { useState, useEffect } from 'react';
import { X, Save, Activity, MapPin, AlignLeft, Info, Thermometer, AlertTriangle, Check, Edit2, Layout } from 'lucide-react';
import DiagramVisualization from '../features/map/DiagramVisualization';
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
  mainGroup?: string;
  subGroup?: string;
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
  const [notes, setNotes] = useState(() => localStorage.getItem(`notes_${segment.id}`) || '');

  
  const [chartData, setChartData] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState<'chart' | 'pid'>('chart');

  const handleSaveRename = () => {
    if (onRename && editName.trim() !== '') {
      onRename(segment.id, editName);
    }
    setIsEditing(false);
  };

  const [relatedLogs, setRelatedLogs] = useState<{id: string, time: string, msg: string, type: string}[]>([]);

  useEffect(() => {
    let isMounted = true;
    import('@tauri-apps/api/core').then(({ invoke }) => {
      const fetchData = async () => {
        if (!segment.dts_ch || !segment.dts_code) return;
        try {
          const data = await invoke<any[]>('get_segment_history', { dtsCh: segment.dts_ch, dtsCode: segment.dts_code, minutes: 30 });
          const alarms = await invoke<any[]>('get_alarms');
          if (isMounted) {
            setChartData(data);
            const filteredAlarms = alarms.filter((a: any) => a.ch === segment.dts_ch && a.code === segment.dts_code);
            const mappedLogs = filteredAlarms.map((a: any) => {
              let logType = 'info';
              let msg = `Event at ${a.distance}m. Temp: ${a.temp}°C`;
              if (a.alarm_type === 2) { logType = 'error'; msg = `CRITICAL OVERHEAT DETECTED at ${a.distance}m! Temperature reached ${a.temp}°C`; }
              else if (a.alarm_type === 1) { logType = 'warn'; msg = `Warning threshold exceeded at ${a.distance}m (${a.temp}°C)`; }
              else if (a.alarm_type === 4) { logType = 'error'; msg = `FIBER BREAK DETECTED at ${a.distance}m!`; }
              return { id: `L-${a.id}`, time: new Date(a.time).toLocaleTimeString(), msg, type: logType };
            });
            setRelatedLogs(mappedLogs);
          }
        } catch (err) {
          console.error("Failed to fetch chart data", err);
        }
      };

      fetchData();
      const timer = setInterval(fetchData, 5000);
      return () => { isMounted = false; clearInterval(timer); };
    });
  }, [segment.dts_ch, segment.dts_code]);

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
                <span className="text-xs font-bold text-text-secondary uppercase tracking-widest flex items-center"><AlignLeft size={14} className="mr-2" /> Group / Sub</span>
                <div className="flex flex-col items-end">
                   <span className="font-mono text-text-primary font-bold">{(segment as any).mainGroup || 'Unassigned'}</span>
                   {(segment as any).subGroup && <span className="text-[10px] font-mono text-text-secondary bg-bg-surface px-1.5 py-0.5 rounded border border-border mt-1">{(segment as any).subGroup}</span>}
                </div>
              </div>
              
              <div className="pt-4 border-t border-border/50 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-text-secondary uppercase tracking-widest flex items-center"><Thermometer size={14} className="mr-2" /> Avg Temp</span>
                  <span className="text-text-primary font-mono font-bold">{segment.temp_avg ?? '-'}°C</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-text-secondary uppercase tracking-widest flex items-center"><Thermometer size={14} className="mr-2" /> Min Temp</span>
                  <div className="text-right">
                    <span className="text-blue-400 font-mono font-bold">{segment.temp_min ?? '-'}°C</span>
                    <p className="text-[10px] text-text-secondary font-mono">at {segment.temp_min_p ?? '-'}m</p>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-text-secondary uppercase tracking-widest flex items-center"><Thermometer size={14} className="mr-2" /> Max Temp</span>
                  <div className="text-right">
                    <span className="text-scada-primary font-mono font-bold text-lg">{segment.temp_max ?? segment.temp}°C</span>
                    <p className="text-[10px] text-text-secondary font-mono">at {segment.temp_max_p ?? '-'}m</p>
                  </div>
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
                  <button onClick={() => localStorage.setItem(`notes_${segment.id}`, notes)} className="w-full bg-scada-primary/20 hover:bg-scada-primary text-scada-primary hover:text-white border border-scada-primary/50 transition-colors py-2 rounded-lg text-sm font-bold flex items-center justify-center">
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
            
            {/* View Mode Toggle & Content */}
            <div className="h-[55%] flex flex-col bg-bg-base border border-border rounded-xl p-0 shadow-inner overflow-hidden">
              <div className="flex border-b border-border bg-bg-surface">
                <button 
                  onClick={() => setActiveTab('chart')} 
                  className={`flex-1 py-3 text-xs font-bold tracking-widest flex items-center justify-center transition-colors ${activeTab === 'chart' ? 'bg-bg-base text-scada-primary border-b-2 border-scada-primary' : 'text-text-secondary hover:text-text-primary'}`}
                >
                  <Activity size={16} className="mr-2" /> RIWAYAT SUHU (30m)
                </button>
                <button 
                  onClick={() => setActiveTab('pid')} 
                  className={`flex-1 py-3 text-xs font-bold tracking-widest flex items-center justify-center transition-colors ${activeTab === 'pid' ? 'bg-bg-base text-scada-primary border-b-2 border-scada-primary' : 'text-text-secondary hover:text-text-primary'}`}
                >
                  <Layout size={16} className="mr-2" /> P&ID DIAGRAM
                </button>
              </div>
              
              <div className="flex-1 w-full min-h-0 relative p-4">
                {activeTab === 'chart' ? (
                   <ResponsiveContainer width="100%" height="100%">
                     <RechartsLineChart data={chartData} margin={{ top: 5, right: 20, left: -20, bottom: 0 }}>
                       <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" opacity={0.3} />
                       <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} tickMargin={10} />
                       <YAxis stroke="#9ca3af" fontSize={12} domain={[0, 100]} />
                       <RechartsTooltip 
                         contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', fontSize: '12px' }}
                         itemStyle={{ color: '#43b581' }}
                       />
                       <Line type="monotone" dataKey="temp" stroke="#43b581" strokeWidth={2} dot={false} activeDot={{ r: 6, fill: '#43b581' }} connectNulls={true} />
                     </RechartsLineChart>
                   </ResponsiveContainer>
                ) : (
                   <div className="absolute inset-0">
                     <DiagramVisualization 
                        isFullscreen={true} 
                        hideHeader={true}
                        alwaysShowPin={true}
                        warningThreshold={45}
                        criticalThreshold={60}
                        segments={[{
                          main_group: segment.mainGroup || '',
                          sub_group: segment.subGroup || null,
                          start_m: segment.start_m,
                          end_m: segment.end_m,
                          temp_max: segment.temp_max ?? segment.temp,
                          temp_avg: segment.temp_avg ?? segment.temp,
                        }]}
                     />
                   </div>
                )}
              </div>
            </div>

            {/* Related Logs */}
            <div className="h-[45%] flex flex-col bg-bg-base border border-border rounded-xl p-5 shadow-inner min-h-0">
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
