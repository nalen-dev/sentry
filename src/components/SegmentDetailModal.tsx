import { useState } from 'react';
import { X, Image as ImageIcon, Camera, Save, Activity, MapPin, AlignLeft, Info, Thermometer, AlertTriangle } from 'lucide-react';
import { LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';

export interface SegmentData {
  id: string;
  name: string;
  distance: string;
  temp: string;
  isAlarm: boolean;
  group?: string;
  areaLocation?: string;
  notes?: string;
  photoUrl?: string;
  // new mapping fields
  mappingId?: number;
  original_name?: string;
}

interface SegmentDetailModalProps {
  segment: SegmentData;
  onClose: () => void;
  userRole?: string;
  onRename?: (id: number, newName: string) => void;
}

type Props = SegmentDetailModalProps;

export default function SegmentDetailModal({ segment, onClose, userRole, onRename }: Props) {
  const isAdmin = userRole === 'ADMINISTRATOR';
  const [notes, setNotes] = useState(segment.notes || '');
  const [name, setName] = useState(segment.name);
  const [isEditingName, setIsEditingName] = useState(false);

  // Dummy Chart Data for the modal
  const dummyChartData = [
    { time: '13:00', temp: parseFloat(segment.temp) - 5 },
    { time: '13:10', temp: parseFloat(segment.temp) - 2 },
    { time: '13:20', temp: parseFloat(segment.temp) + 1 },
    { time: '13:30', temp: parseFloat(segment.temp) - 1 },
    { time: '13:40', temp: parseFloat(segment.temp) + 4 },
    { time: '13:50', temp: parseFloat(segment.temp) },
  ];

  // Dummy Related Logs
  const relatedLogs = [
    { id: 1, time: '13:45', msg: `Temperature spike detected in ${segment.name}`, type: segment.isAlarm ? 'error' : 'warn' },
    { id: 2, time: '13:30', msg: `Routine sweep completed for ${segment.group || 'BC Main-01'}`, type: 'info' },
    { id: 3, time: '12:00', msg: `Calibration adjusted for area ${segment.areaLocation || 'Tunnel A'}`, type: 'info' },
  ];

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-6xl h-[85vh] bg-bg-panel border border-border rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        
        {/* HEADER */}
        <div className="flex justify-between items-start p-6 border-b border-border bg-bg-surface/50">
          <div className="flex items-center">
            <div className={`p-4 rounded-xl mr-5 shadow-inner border ${segment.isAlarm ? 'bg-bg-alarm border-red-500/50' : 'bg-bg-base border-border'}`}>
              <AlertTriangle size={32} className={`${segment.isAlarm ? 'text-red-500 animate-pulse' : 'text-scada-primary'}`} />
            </div>
            <div>
              {isEditingName && isAdmin ? (
                <div className="flex items-center space-x-2">
                  <input 
                    type="text" 
                    value={name} 
                    onChange={e => setName(e.target.value)}
                    className="bg-bg-base border border-scada-primary rounded px-2 py-1 text-2xl font-bold text-text-primary focus:outline-none"
                    autoFocus
                  />
                  <button 
                    onClick={() => {
                      setIsEditingName(false);
                      if (onRename && segment.mappingId) onRename(segment.mappingId, name);
                    }}
                    className="p-2 bg-scada-primary/20 text-scada-primary rounded hover:bg-scada-primary hover:text-white transition-colors"
                  >
                    <Save size={18} />
                  </button>
                </div>
              ) : (
                <h2 className="text-2xl font-bold text-text-primary tracking-wider flex items-center">
                  {name}
                  {isAdmin && (
                    <button onClick={() => setIsEditingName(true)} className="ml-3 text-text-secondary hover:text-scada-primary text-sm transition-colors uppercase tracking-widest bg-bg-base px-2 py-1 rounded border border-border">
                      Rename
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
                <span className="font-mono text-text-primary">{segment.distance} to Ops Room</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-text-secondary uppercase tracking-widest flex items-center"><AlignLeft size={14} className="mr-2" /> Group</span>
                <span className="font-mono text-text-primary">{segment.group || 'BC MAIN - 01'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-text-secondary uppercase tracking-widest flex items-center"><MapPin size={14} className="mr-2" /> Area</span>
                <span className="font-mono text-text-primary">{segment.areaLocation || 'Zone Alpha'}</span>
              </div>
              <div className="flex items-center justify-between pt-4 border-t border-border/50">
                <span className="text-xs font-bold text-text-secondary uppercase tracking-widest flex items-center"><Thermometer size={14} className="mr-2" /> Current Temp</span>
                <span className={`text-2xl font-mono font-bold ${segment.isAlarm ? 'text-red-400' : 'text-scada-success'}`}>{segment.temp}°C</span>
              </div>
            </div>

            {/* Photo Section */}
            <div className="p-6 border-b border-border flex flex-col">
              <span className="text-xs font-bold text-text-secondary uppercase tracking-widest mb-3 flex items-center"><ImageIcon size={14} className="mr-2" /> Segment Photo</span>
              <div className="w-full h-48 bg-bg-surface border-2 border-dashed border-border rounded-xl flex flex-col items-center justify-center text-text-secondary hover:text-scada-primary hover:border-scada-primary transition-colors cursor-pointer group">
                {segment.photoUrl ? (
                  <img src={segment.photoUrl} alt="Segment" className="w-full h-full object-cover rounded-xl" />
                ) : (
                  <>
                    <Camera size={32} className="mb-2 group-hover:scale-110 transition-transform" />
                    <span className="text-sm font-bold">Add Photo</span>
                  </>
                )}
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
              <span className="text-xs font-bold text-text-primary uppercase tracking-widest mb-4 flex items-center"><Activity size={16} className="mr-2 text-scada-primary" /> Temperature Trend (Last 1 Hour)</span>
              <div className="flex-1 w-full min-h-0">
                 <ResponsiveContainer width="100%" height="100%">
                   <RechartsLineChart data={dummyChartData} margin={{ top: 5, right: 20, left: -20, bottom: 0 }}>
                     <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" opacity={0.3} />
                     <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} tickMargin={10} />
                     <YAxis stroke="#9ca3af" fontSize={12} domain={['dataMin - 10', 'dataMax + 10']} />
                     <RechartsTooltip 
                       contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', fontSize: '12px' }}
                       itemStyle={{ color: '#06b6d4', fontWeight: 'bold' }}
                       labelStyle={{ color: 'var(--text-secondary)' }}
                     />
                     <Line type="monotone" dataKey="temp" stroke="#06b6d4" strokeWidth={3} dot={{ r: 4, fill: '#06b6d4', strokeWidth: 0 }} activeDot={{ r: 6, strokeWidth: 0 }} />
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
