import re

with open('src/components/SegmentDetailModal.tsx', 'r') as f:
    content = f.read()

# Add get_system_logs invoke
if "invoke<any[]>('get_system_logs')" not in content:
    effect_old = """          const data = await invoke<any[]>('get_segment_history', { dtsCh: segment.dts_ch, dtsCode: segment.dts_code, minutes: 30 });
          setChartData(data);
          
          if (Array.isArray(data) && data.length > 0) {
            const temps = data.map(d => d.temp).filter(t => t > 0);
            if (temps.length > 0) {
               setStats({
                 max: Math.max(...temps),
                 min: Math.min(...temps),
                 avg: temps.reduce((a,b) => a+b, 0) / temps.length
               });
            }
          }
          
          // Get specific alarms for this segment
          const alarms = await invoke<any[]>('get_alarms', { date: null });
          if (isMounted) {
            const filteredAlarms = alarms.filter((a: any) => a.ch === segment.dts_ch && a.code === segment.dts_code);
            setSegmentAlarms(filteredAlarms);
          }"""

    effect_new = """          const [data, alarms, sysLogs] = await Promise.all([
             invoke<any[]>('get_segment_history', { dtsCh: segment.dts_ch, dtsCode: segment.dts_code, minutes: 30 }),
             invoke<any[]>('get_alarms', { date: null }),
             invoke<any[]>('get_system_logs').catch(() => [])
          ]);
          setChartData(data);
          
          if (Array.isArray(data) && data.length > 0) {
            const temps = data.map(d => d.temp).filter(t => t > 0);
            if (temps.length > 0) {
               setStats({
                 max: Math.max(...temps),
                 min: Math.min(...temps),
                 avg: temps.reduce((a,b) => a+b, 0) / temps.length
               });
            }
          }
          
          if (isMounted) {
            const filteredHw = alarms
                .filter((a: any) => a.ch === segment.dts_ch && a.code === segment.dts_code)
                .map((a: any) => ({
                   id: a.id,
                   rawTime: new Date(a.time),
                   time: new Date(a.time).toLocaleTimeString(),
                   msg: `Event at ${a.distance}m. Temp: ${a.temp}°C`,
                   type: a.alarm_type === 2 ? 'error' : a.alarm_type === 4 ? 'error' : 'warn',
                   source: 'DTS-UNIT'
                }));
                
            const segName = segment.name || segment.original_name;
            const filteredSys = sysLogs
                .filter((s: any) => s.message.includes(segName))
                .map((s: any) => ({
                   id: s.id + 100000,
                   rawTime: new Date(s.timestamp),
                   time: new Date(s.timestamp).toLocaleTimeString(),
                   msg: s.message,
                   type: s.event_type === 'ALARM' ? 'error' : s.event_type === 'WARNING' ? 'warn' : 'info',
                   source: 'SENTRY CORE'
                }));
                
            const combined = [...filteredHw, ...filteredSys].sort((a, b) => b.rawTime.getTime() - a.rawTime.getTime());
            setSegmentAlarms(combined);
          }"""

    content = content.replace(effect_old, effect_new)
    
    # Update rendering logic
    render_old = """                  {segmentAlarms.length === 0 ? (
                    <div className="flex items-center justify-center h-32 text-text-secondary text-sm font-mono">
                      Belum ada peringatan untuk segment ini.
                    </div>
                  ) : (
                    segmentAlarms.map((alarm, idx) => (
                      <div key={idx} className="flex flex-col p-3 rounded-lg bg-bg-base border border-border/50 hover:bg-bg-panel transition-colors">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-mono text-text-secondary">{new Date(alarm.time).toLocaleString()}</span>
                          <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                            alarm.alarm_type === 2 ? 'bg-red-500/20 text-red-500' : 'bg-yellow-500/20 text-yellow-500'
                          }`}>
                            {alarm.alarm_type === 2 ? 'ALARM' : 'WARNING'}
                          </span>
                        </div>
                        <p className="text-sm text-text-primary">
                          {alarm.alarm_type === 4 ? 'FIBER BREAK DETECTED!' : `Suhu mencapai ${alarm.temp}°C pada jarak ${alarm.distance}m.`}
                        </p>
                      </div>
                    ))
                  )}"""

    render_new = """                  {segmentAlarms.length === 0 ? (
                    <div className="flex items-center justify-center h-32 text-text-secondary text-sm font-mono">
                      Belum ada peringatan untuk segment ini.
                    </div>
                  ) : (
                    segmentAlarms.map((alarm, idx) => (
                      <div key={idx} className="flex flex-col p-3 rounded-lg bg-bg-base border border-border/50 hover:bg-bg-panel transition-colors">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-mono text-text-secondary">{alarm.time}</span>
                          <div className="flex space-x-2">
                            <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                              alarm.type === 'error' ? 'bg-red-500/20 text-red-500' : alarm.type === 'warn' ? 'bg-yellow-500/20 text-yellow-500' : 'bg-blue-500/20 text-blue-400'
                            }`}>
                              {alarm.type === 'error' ? 'ALARM' : alarm.type === 'warn' ? 'WARNING' : 'INFO'}
                            </span>
                            <span className="text-[10px] px-2 py-0.5 rounded font-bold uppercase bg-bg-panel text-text-secondary border border-border">
                              {alarm.source}
                            </span>
                          </div>
                        </div>
                        <p className="text-sm text-text-primary">
                          {alarm.msg}
                        </p>
                      </div>
                    ))
                  )}"""

    content = content.replace(render_old, render_new)

    with open('src/components/SegmentDetailModal.tsx', 'w') as f:
        f.write(content)

