import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

# 1. Add global variable outside component
if "const globalAlarmState" not in content:
    content = content.replace(
        "export default function Dashboard({ isFullscreen, setMapZoom }: DashboardProps) {",
        "const globalAlarmState: Record<number, 'normal'|'warning'|'danger'> = {};\n\nexport default function Dashboard({ isFullscreen, setMapZoom }: DashboardProps) {"
    )

# 2. Replace alarmStateRef with globalAlarmState and fix the logic
old_logic = """  // Track system logs for custom thresholds
  const alarmStateRef = useRef<Record<number, 'normal'|'warning'|'danger'>>({});
  
  useEffect(() => {
    if (mappings.length === 0) return;
    import('@tauri-apps/api/core').then(({ invoke }) => {
      mappings.forEach(seg => {
        const temp = seg.temp_max || 0;
        let currentState: 'normal'|'warning'|'danger' = 'normal';
        if (temp >= criticalThreshold) currentState = 'danger';
        else if (temp >= warningThreshold) currentState = 'warning';
        
        const prevState = alarmStateRef.current[seg.id] || 'normal';
        
        if (currentState !== prevState) {
           alarmStateRef.current[seg.id] = currentState;
           const name = seg.custom_name || seg.original_name;
           if (currentState === 'danger' && prevState !== 'danger') {
              invoke('write_system_log', { eventType: 'ALARM', message: `CRITICAL DANGER: Segmen ${name} mencapai suhu ${temp}°C (Batas: ${criticalThreshold}°C)` }).catch(console.error);
           } else if (currentState === 'warning' && prevState !== 'warning' && prevState !== 'danger') {
              invoke('write_system_log', { eventType: 'ALARM', message: `WARNING: Segmen ${name} mencapai suhu ${temp}°C (Batas: ${warningThreshold}°C)` }).catch(console.error);
           } else if (currentState === 'normal' && prevState !== 'normal') {
              invoke('write_system_log', { eventType: 'INFO', message: `CLEAR: Segmen ${name} kembali normal pada suhu ${temp}°C` }).catch(console.error);
           }
        }
      });
    });
  }, [mappings, warningThreshold, criticalThreshold]);"""

new_logic = """  // Track system logs for custom thresholds (using global state to survive unmounts)
  useEffect(() => {
    if (mappings.length === 0) return;
    import('@tauri-apps/api/core').then(({ invoke }) => {
      mappings.forEach(seg => {
        const temp = seg.temp_max || 0;
        let currentState: 'normal'|'warning'|'danger' = 'normal';
        
        // Add a slight 0.5 degree deadband to prevent rapid toggling
        const prevState = globalAlarmState[seg.id] || 'normal';
        
        if (temp >= criticalThreshold) currentState = 'danger';
        else if (temp >= warningThreshold && (prevState === 'danger' ? temp > warningThreshold + 0.5 : true)) currentState = 'warning';
        else if (temp < warningThreshold - 0.5) currentState = 'normal';
        else currentState = prevState; // stay in previous state if inside the 0.5 deadband gap
        
        if (currentState !== prevState) {
           globalAlarmState[seg.id] = currentState;
           const name = seg.custom_name || seg.original_name;
           
           if (currentState === 'danger') {
              invoke('write_system_log', { eventType: 'ALARM', message: `CRITICAL DANGER: Segmen ${name} menyentuh suhu ${temp.toFixed(1)}°C (Batas: ${criticalThreshold}°C)` }).catch(console.error);
           } else if (currentState === 'warning') {
              if (prevState === 'danger') {
                  invoke('write_system_log', { eventType: 'WARNING', message: `DOWNGRADE: Suhu Segmen ${name} turun ke level Warning (${temp.toFixed(1)}°C)` }).catch(console.error);
              } else {
                  invoke('write_system_log', { eventType: 'WARNING', message: `WARNING: Segmen ${name} menyentuh suhu ${temp.toFixed(1)}°C (Batas: ${warningThreshold}°C)` }).catch(console.error);
              }
           } else if (currentState === 'normal') {
              invoke('write_system_log', { eventType: 'INFO', message: `CLEAR: Segmen ${name} kembali Normal pada suhu ${temp.toFixed(1)}°C` }).catch(console.error);
           }
        }
      });
    });
  }, [mappings, warningThreshold, criticalThreshold]);"""

content = content.replace(old_logic, new_logic)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)

