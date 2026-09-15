import re

with open('src/features/dashboard/SegmentStats.tsx', 'r') as f:
    ss = f.read()

old_props = """interface SegmentStatsProps {
  totalSegments: number;
  normalSegments: number;
  highTempSegments: number;
  fiberBreakSegments: number;
  onCategoryClick: (category: 'Total' | 'Normal' | 'HighTemp' | 'FiberBreak') => void;
}"""

new_props = """interface SegmentStatsProps {
  totalSegments: number;
  normalSegments: number;
  warningSegments: number;
  dangerSegments: number;
  onCategoryClick: (category: 'Total' | 'Normal' | 'Warning' | 'Danger') => void;
}"""
ss = ss.replace(old_props, new_props)

old_comp_args = """export default function SegmentStats({
  totalSegments,
  normalSegments,
  highTempSegments,
  fiberBreakSegments,
  onCategoryClick
}: SegmentStatsProps) {"""

new_comp_args = """export default function SegmentStats({
  totalSegments,
  normalSegments,
  warningSegments,
  dangerSegments,
  onCategoryClick
}: SegmentStatsProps) {"""
ss = ss.replace(old_comp_args, new_comp_args)

old_danger_check = """const isDanger = highTempSegments > 0 || fiberBreakSegments > 0;"""
new_danger_check = """const isDanger = dangerSegments > 0;"""
ss = ss.replace(old_danger_check, new_danger_check)

old_boxes = """        <div 
          onClick={() => onCategoryClick('HighTemp')}
          className="flex flex-col bg-bg-surface hover:bg-bg-base p-2 rounded border border-orange-500/30 cursor-pointer transition-colors"
        >
          <span className="text-lg font-mono font-bold text-orange-500">{highTempSegments}</span>
          <span className="text-[8px] text-orange-400 uppercase font-bold tracking-widest mt-1">High Temp</span>
        </div>
        <div 
          onClick={() => onCategoryClick('FiberBreak')}
          className="flex flex-col bg-bg-alarm/50 hover:bg-bg-alarm/80 p-2 rounded border border-red-500/30 cursor-pointer transition-colors"
        >
          <span className="text-lg font-mono font-bold text-red-500">{fiberBreakSegments}</span>
          <span className="text-[8px] text-red-400 uppercase font-bold tracking-widest mt-1">Fiber Break</span>
        </div>"""

new_boxes = """        <div 
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
        </div>"""
ss = ss.replace(old_boxes, new_boxes)

with open('src/features/dashboard/SegmentStats.tsx', 'w') as f:
    f.write(ss)
