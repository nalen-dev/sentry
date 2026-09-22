import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

old_block = """        <LogPanel 
          isFullscreen={isFullscreen}
          dummyLogs={alarms.map(a => ({
            id: a.id,
            time: new Date(a.time).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
            msg: `Ch${a.ch}-C${a.code} at ${a.distance}m: ${a.alarm_type === 1 ? 'High Temp' : a.alarm_type === 2 ? 'Low Temp' : a.alarm_type === 3 ? 'Temp Rise' : a.alarm_type === 4 ? 'Fiber Break' : 'Anti-tamper'} (${a.temp}°C)`,
            type: a.is_active ? 'error' : 'info'
          }))}
          currentTime={currentTime}
        />"""

new_block = """        <LogPanel 
          isFullscreen={isFullscreen}
          dummyLogs={[
            ...alarms.map(a => ({
              id: a.id,
              rawTime: new Date(a.time),
              time: new Date(a.time).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
              msg: `[DTS] Ch${a.ch}-C${a.code} at ${a.distance}m: ${a.temp}°C`,
              type: a.is_active ? 'error' : 'info'
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

content = content.replace(old_block, new_block)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)

