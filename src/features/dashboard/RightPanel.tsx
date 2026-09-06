import { Activity, LineChart as LineChartIcon } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface RightPanelProps {
  totalSegments: number;
  normalSegments: number;
  warningSegments: number;
  dangerSegments: number;
  dummyChartData: { time: string; temp: number }[];
}

export default function RightPanel({
  totalSegments,
  normalSegments,
  warningSegments,
  dangerSegments,
  dummyChartData
}: RightPanelProps) {
  return (
    <>
      {/* SYSTEM STATISTICS */}
      <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl p-4 shadow-lg pointer-events-auto shrink-0 flex flex-col mt-4">
        <div className="text-sm font-bold text-text-primary uppercase tracking-widest flex items-center border-b border-border pb-2 mb-3">
          <Activity size={16} className="mr-2 text-scada-primary" /> SEGMENT STATS
        </div>
        <div className="grid grid-cols-4 gap-2 text-center">
          <div className="flex flex-col bg-bg-surface p-2 rounded border border-border">
            <span className="text-lg font-mono font-bold text-text-primary">{totalSegments}</span>
            <span className="text-[9px] text-text-secondary uppercase font-bold tracking-widest mt-1">Total</span>
          </div>
          <div className="flex flex-col bg-bg-surface p-2 rounded border border-border">
            <span className="text-lg font-mono font-bold text-scada-success">{normalSegments}</span>
            <span className="text-[9px] text-text-secondary uppercase font-bold tracking-widest mt-1">Normal</span>
          </div>
          <div className="flex flex-col bg-bg-surface p-2 rounded border border-border">
            <span className="text-lg font-mono font-bold text-yellow-500">{warningSegments}</span>
            <span className="text-[9px] text-text-secondary uppercase font-bold tracking-widest mt-1">Warn</span>
          </div>
          <div className="flex flex-col bg-bg-alarm/50 p-2 rounded border border-red-500/30">
            <span className="text-lg font-mono font-bold text-red-500">{dangerSegments}</span>
            <span className="text-[9px] text-red-400 uppercase font-bold tracking-widest mt-1">Danger</span>
          </div>
        </div>
      </div>

      {/* TEMPERATURE CHART */}
      <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl p-4 shadow-lg pointer-events-auto flex-1 flex flex-col min-h-0 mt-4">
        <div className="text-sm font-bold text-text-primary uppercase tracking-widest flex items-center border-b border-border pb-2 mb-3 shrink-0">
          <LineChartIcon size={16} className="mr-2 text-scada-primary" /> TEMPERATURE TREND
        </div>
        <div className="flex-1 w-full min-h-0">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={dummyChartData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" opacity={0.3} />
              <XAxis dataKey="time" stroke="#9ca3af" fontSize={10} tickMargin={5} />
              <YAxis stroke="#9ca3af" fontSize={10} />
              <Tooltip 
                contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', fontSize: '12px' }}
                itemStyle={{ color: '#06b6d4', fontWeight: 'bold' }}
                labelStyle={{ color: 'var(--text-secondary)' }}
              />
              <Line type="monotone" dataKey="temp" stroke="#06b6d4" strokeWidth={2} dot={{ r: 3, fill: '#06b6d4', strokeWidth: 0 }} activeDot={{ r: 5, strokeWidth: 0 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </>
  );
}
