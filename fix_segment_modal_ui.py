import re

with open('src/components/SegmentDetailModal.tsx', 'r') as f:
    sm = f.read()

# Replace the stats block
old_stats = """              <div className="pt-4 border-t border-border/50 space-y-3">
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
              </div>"""

new_stats = """              <div className="pt-4 border-t border-border/50 space-y-3">
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
              </div>"""

sm = sm.replace(old_stats, new_stats)

with open('src/components/SegmentDetailModal.tsx', 'w') as f:
    f.write(sm)

