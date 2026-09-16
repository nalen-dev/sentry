import re

with open('src/pages/LogsPage.tsx', 'r') as f:
    code = f.read()

# 1. Add imports
code = code.replace("import { useState } from 'react';", "import { useState, useEffect } from 'react';\nimport { invoke } from '@tauri-apps/api/core';")

# 2. Modify DUMMY_HISTORY_LOGS to use state
old_dummy = """const DUMMY_HISTORY_LOGS: SystemLog[] = [
  { id: 'L-1049', type: 'error', timestamp: new Date(Date.now() - 1000 * 60 * 5), segment: 'TCM16 - TN12', msg: 'CRITICAL OVERHEAT DETECTED! Temperature reached 68.4°C', user: 'SYSTEM' },
  { id: 'L-1048', type: 'warn', timestamp: new Date(Date.now() - 1000 * 60 * 15), segment: 'BEK56 - BEK56M', msg: 'Warning threshold exceeded (46.2°C)', user: 'SYSTEM' },
  { id: 'L-1047', type: 'info', timestamp: new Date(Date.now() - 1000 * 60 * 60), segment: 'SYSTEM', msg: 'DTS Calibration synchronized successfully', user: 'OP-7729' },
  { id: 'L-1046', type: 'error', timestamp: new Date(Date.now() - 1000 * 60 * 120), segment: 'TCM16 - TN45', msg: 'FIBER BREAK DETECTED. Distance: 340m', user: 'SYSTEM' },
  { id: 'L-1045', type: 'info', timestamp: new Date(Date.now() - 1000 * 60 * 240), segment: 'SYSTEM', msg: 'System reboot initiated', user: 'ADMIN' },
  { id: 'L-1044', type: 'warn', timestamp: new Date(Date.now() - 1000 * 60 * 480), segment: 'BC4 A', msg: 'Temperature rising rapidly (+5°C/min)', user: 'SYSTEM' },
];

export default function LogsPage() {"""

new_dummy = """export default function LogsPage() {
  const [logs, setLogs] = useState<SystemLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const fetchLogs = async () => {
      try {
        const alarms: any[] = await invoke('get_alarms');
        const mappings: any[] = await invoke('get_segment_mappings');
        
        if (!isMounted) return;

        const mappedLogs: SystemLog[] = alarms.map((a: any) => {
          const map = mappings.find(m => m.dts_ch === a.ch && m.dts_code === a.code);
          const segmentName = map && map.main_group !== 'Unassigned' ? `${map.main_group} ${map.sub_group ? '- ' + map.sub_group : ''}` : `CH ${a.ch} CODE ${a.code}`;
          
          let logType: 'error' | 'warn' | 'info' = 'info';
          let msg = `Event at ${a.distance}m. Temp: ${a.temp}°C`;
          
          if (a.alarm_type === 2) {
             logType = 'error';
             msg = `CRITICAL OVERHEAT DETECTED at ${a.distance}m! Temperature reached ${a.temp}°C`;
          } else if (a.alarm_type === 1) {
             logType = 'warn';
             msg = `Warning threshold exceeded at ${a.distance}m (${a.temp}°C)`;
          } else if (a.alarm_type === 4) {
             logType = 'error';
             msg = `FIBER BREAK DETECTED at ${a.distance}m!`;
          }

          return {
            id: `L-${a.id}`,
            type: logType,
            timestamp: new Date(a.time),
            segment: segmentName,
            msg: msg,
            user: 'SYSTEM'
          };
        });
        
        setLogs(mappedLogs);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setLoading(false);
      }
    };
    
    fetchLogs();
  }, []);"""

code = code.replace(old_dummy, new_dummy)

# 3. Use state logs instead of DUMMY_HISTORY_LOGS
code = code.replace("DUMMY_HISTORY_LOGS.filter", "logs.filter")
code = code.replace("DUMMY_HISTORY_LOGS.length", "logs.length")

with open('src/pages/LogsPage.tsx', 'w') as f:
    f.write(code)

