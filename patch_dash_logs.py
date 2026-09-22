import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

# 1. Add sysLogs state
state_old = "const [alarms, setAlarms] = useState<AlarmLog[]>([]);"
state_new = "const [alarms, setAlarms] = useState<AlarmLog[]>([]);\n  const [sysLogs, setSysLogs] = useState<any[]>([]);"
content = content.replace(state_old, state_new)

# 2. Add sysLogs to fetchLive
fetch_old = """          Promise.all([
            invoke<LiveSegment[]>('get_live_segments'),
            invoke<AlarmLog[]>('get_alarms')
          ]).then(([m, a]) => {"""

fetch_new = """          Promise.all([
            invoke<LiveSegment[]>('get_live_segments'),
            invoke<AlarmLog[]>('get_alarms'),
            invoke<any[]>('get_system_logs').catch(() => [])
          ]).then(([m, a, sys]) => {"""
content = content.replace(fetch_old, fetch_new)

set_old = """            setMappings(m);
            setAlarms(a);"""
set_new = """            setMappings(m);
            setAlarms(a);
            setSysLogs(sys);"""
content = content.replace(set_old, set_new)

# 3. Modify dummyLogs logic
logpanel_old = """        <LogPanel 
          isFullscreen={isFullscreen}
          dummyLogs={alarms.map(a => ({
            id: a.id,
            time: new Date(a.time).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
            msg: `Ch${a.ch}-C${a.code} at ${a.distance}m: ${a.alarm_type === 1 ? 'High Temp' : a.alarm_type === 2 ? 'Low Temp' : a.alarm_type === 3 ? 'Temp Rise' : a.alarm_type === 4 ? 'Fiber Break' : 'Anti-tamper'} (${a.temp}°C)`,
            type: a.alarm_type === 2 ? 'error' : a.alarm_type === 4 ? 'error' : 'warning'
          }))}
          currentTime={currentTime}
        />"""

logpanel_new = """        <LogPanel 
          isFullscreen={isFullscreen}
          dummyLogs={[
            ...alarms.map(a => ({
              id: a.id,
              rawTime: new Date(a.time),
              time: new Date(a.time).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
              msg: `[DTS] Ch${a.ch}-C${a.code} at ${a.distance}m: ${a.alarm_type === 1 ? 'High Temp' : a.alarm_type === 2 ? 'Low Temp' : a.alarm_type === 3 ? 'Temp Rise' : a.alarm_type === 4 ? 'Fiber Break' : 'Anti-tamper'} (${a.temp}°C)`,
              type: a.alarm_type === 2 ? 'error' : a.alarm_type === 4 ? 'error' : 'warning'
            })),
            ...sysLogs.map(s => ({
              id: s.id + 100000,
              rawTime: new Date(s.timestamp),
              time: new Date(s.timestamp).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
              msg: `[SYS] ${s.message}`,
              type: s.event_type === 'ALARM' ? 'error' : s.event_type === 'WARNING' ? 'warning' : 'info'
            }))
          ].sort((a, b) => b.rawTime.getTime() - a.rawTime.getTime()).slice(0, 10)}
          currentTime={currentTime}
        />"""
content = content.replace(logpanel_old, logpanel_new)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)

