import { Activity } from 'lucide-react';

interface SegmentStatsProps {
  totalSegments: number;
  normalSegments: number;
  warningSegments: number;
  dangerSegments: number;
  onCategoryClick: (category: 'Total' | 'Normal' | 'Warning' | 'Danger') => void;
}

export default function SegmentStats({
  totalSegments,
  normalSegments,
  warningSegments,
  dangerSegments,
  onCategoryClick
}: SegmentStatsProps) {
  const isDanger = dangerSegments > 0;
  
  return (
    <div className={`bg-bg-panel/95 backdrop-blur-md border rounded-xl p-4 shadow-lg pointer-events-auto shrink-0 flex flex-col transition-colors duration-300 ${
      isDanger ? 'border-red-500 shadow-[0_0_20px_rgba(239,68,68,0.4)] animate-pulse' : 'border-border'
    }`}>
      <div className="text-sm font-bold text-text-primary uppercase tracking-widest flex items-center border-b border-border pb-2 mb-3">
        <Activity size={16} className={`mr-2 ${isDanger ? 'text-red-500' : 'text-scada-primary'}`} /> SEGMENT STATS
      </div>
      <div className="grid grid-cols-4 gap-2 text-center">
        <div 
          onClick={() => onCategoryClick('Total')}
          className="flex flex-col bg-bg-surface hover:bg-bg-base p-2 rounded border border-border cursor-pointer transition-colors"
        >
          <span className="text-lg font-mono font-bold text-text-primary">{totalSegments}</span>
          <span className="text-[9px] text-text-secondary uppercase font-bold tracking-widest mt-1">Total</span>
        </div>
        <div 
          onClick={() => onCategoryClick('Normal')}
          className="flex flex-col bg-bg-surface hover:bg-bg-base p-2 rounded border border-border cursor-pointer transition-colors"
        >
          <span className="text-lg font-mono font-bold text-scada-success">{normalSegments}</span>
          <span className="text-[9px] text-text-secondary uppercase font-bold tracking-widest mt-1">Normal</span>
        </div>
        <div 
          onClick={() => onCategoryClick('Warning')}
          className="flex flex-col bg-bg-surface hover:bg-bg-base p-2 rounded border border-border cursor-pointer transition-colors"
        >
          <span className="text-lg font-mono font-bold text-yellow-500">{warningSegments}</span>
          <span className="text-[9px] text-text-secondary uppercase font-bold tracking-widest mt-1">Warn</span>
        </div>
        <div 
          onClick={() => onCategoryClick('Danger')}
          className="flex flex-col bg-bg-alarm/50 hover:bg-bg-alarm/80 p-2 rounded border border-red-500/30 cursor-pointer transition-colors"
        >
          <span className="text-lg font-mono font-bold text-red-500">{dangerSegments}</span>
          <span className="text-[9px] text-red-400 uppercase font-bold tracking-widest mt-1">Danger</span>
        </div>
      </div>
    </div>
  );
}
