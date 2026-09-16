import re

with open('src/components/SegmentDetailModal.tsx', 'r') as f:
    code = f.read()

# Replace line chart stroke
code = code.replace('stroke="var(--scada-primary)"', 'stroke="#43b581"')
code = code.replace("fill: 'var(--scada-primary)'", "fill: '#43b581'")
code = code.replace("color: 'var(--scada-primary)'", "color: '#43b581'")

# Fix Notes to use localStorage
old_notes_state = "const [notes, setNotes] = useState('');"
new_notes_state = "const [notes, setNotes] = useState(() => localStorage.getItem(`notes_${segment.id}`) || '');"
code = code.replace(old_notes_state, new_notes_state)

old_save_notes = """<button className="w-full bg-scada-primary/20 hover:bg-scada-primary text-scada-primary hover:text-white border border-scada-primary/50 transition-colors py-2 rounded-lg text-sm font-bold flex items-center justify-center">
                    <Save size={16} className="mr-2" /> SAVE NOTES
                  </button>"""

new_save_notes = """<button onClick={() => localStorage.setItem(`notes_${segment.id}`, notes)} className="w-full bg-scada-primary/20 hover:bg-scada-primary text-scada-primary hover:text-white border border-scada-primary/50 transition-colors py-2 rounded-lg text-sm font-bold flex items-center justify-center">
                    <Save size={16} className="mr-2" /> SAVE NOTES
                  </button>"""
code = code.replace(old_save_notes, new_save_notes)

# Fix Logs to fetch real data
old_logs_def = """const relatedLogs = [
    { id: 1, time: '14:22:00', msg: 'System check normal', type: 'info' },
    { id: 2, time: '12:05:11', msg: 'Slight temp increase detected', type: 'warn' },
    { id: 3, time: '09:00:00', msg: 'Daily reset initiated', type: 'info' },
  ];"""

new_logs_def = """const [relatedLogs, setRelatedLogs] = useState<{id: string, time: string, msg: string, type: string}[]>([]);"""
code = code.replace(old_logs_def, new_logs_def)

# Add logs fetch inside useEffect
old_fetch = """const data = await invoke<any[]>('get_segment_history', { dtsCh: segment.dts_ch, dtsCode: segment.dts_code, minutes: 30 });
          if (isMounted) setChartData(data);"""

new_fetch = """const data = await invoke<any[]>('get_segment_history', { dtsCh: segment.dts_ch, dtsCode: segment.dts_code, minutes: 30 });
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
          }"""
code = code.replace(old_fetch, new_fetch)

# Fix group and subgroup display
old_group = """<span className="text-xs font-bold text-text-secondary uppercase tracking-widest flex items-center"><AlignLeft size={14} className="mr-2" /> Group</span>
                <span className="font-mono text-text-primary">{segment.group || 'BC MAIN - 01'}</span>"""

new_group = """<span className="text-xs font-bold text-text-secondary uppercase tracking-widest flex items-center"><AlignLeft size={14} className="mr-2" /> Group / Sub</span>
                <div className="flex flex-col items-end">
                   <span className="font-mono text-text-primary font-bold">{(segment as any).mainGroup || 'Unassigned'}</span>
                   {(segment as any).subGroup && <span className="text-[10px] font-mono text-text-secondary bg-bg-surface px-1.5 py-0.5 rounded border border-border mt-1">{(segment as any).subGroup}</span>}
                </div>"""
code = code.replace(old_group, new_group)

# Handle relatedLogs mapping in UI (already handled by the type change, but wait, the type has id: string now)

with open('src/components/SegmentDetailModal.tsx', 'w') as f:
    f.write(code)

