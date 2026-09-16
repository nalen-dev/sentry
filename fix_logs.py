import re

with open('src/pages/LogsPage.tsx', 'r') as f:
    code = f.read()

# Replace the whole generateDummyLogs logic and DUMMY_HISTORY_LOGS with the new state and effect
old_start = "const generateDummyLogs = () => {"
old_end = "const [userId, setUserId] = useState('OP-7729');"

# Extract everything between old_start and old_end
start_idx = code.find(old_start)
end_idx = code.find(old_end) + len(old_end)

if start_idx != -1 and end_idx != -1:
    new_code = """
interface SystemLog {
  id: string;
  type: 'info' | 'warn' | 'error';
  timestamp: Date;
  segment: string;
  msg: string;
  user: string;
}

export default function LogsPage() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true;
  });
  const [userRole, setUserRole] = useState('OPERATOR');
  const [userId, setUserId] = useState('OP-7729');
  
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
  }, []);
"""
    code = code[:start_idx] + new_code + code[end_idx:]

with open('src/pages/LogsPage.tsx', 'w') as f:
    f.write(code)

