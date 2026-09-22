import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

# 1. Add useRef
if "import { useState, useEffect, useMemo" not in content:
    content = content.replace("import { useState, useEffect } from 'react';", "import { useState, useEffect, useRef, useMemo } from 'react';")
else:
    content = content.replace("import { useState, useEffect, useMemo } from 'react';", "import { useState, useEffect, useRef, useMemo } from 'react';")

# 2. Add the tracking ref and useEffect
effect_code = """  const [isPopupMuted, setIsPopupMuted] = useState(false);
  
  // Track system logs for custom thresholds
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
  }, [mappings, warningThreshold, criticalThreshold]);
"""

content = content.replace("  const [isPopupMuted, setIsPopupMuted] = useState(false);", effect_code)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)

