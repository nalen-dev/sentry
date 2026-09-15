import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    db = f.read()

# Add thresholds to state
db = db.replace(
    "const [isLiveActive, setIsLiveActive] = useState(false);",
    "const [isLiveActive, setIsLiveActive] = useState(false);\n  const [warningThreshold, setWarningThreshold] = useState(45);\n  const [criticalThreshold, setCriticalThreshold] = useState(60);"
)

# Fetch settings inside initial fetch
old_fetch = """        const alarmsData = await invoke<any[]>('get_alarms');
        setAlarms(alarmsData);"""
        
new_fetch = """        const alarmsData = await invoke<any[]>('get_alarms');
        setAlarms(alarmsData);
        
        const settings = await invoke<Record<string, string>>('get_all_settings');
        if (settings['warning_threshold']) setWarningThreshold(Number(settings['warning_threshold']));
        if (settings['critical_threshold']) setCriticalThreshold(Number(settings['critical_threshold']));"""

db = db.replace(old_fetch, new_fetch)

# Update baseAreas mapping
old_base_areas = """  const baseAreas: (SegmentData & { mainGroup: string; subGroup: string | null })[] = mappings.map(m => ({
        id: m.id,
        name: m.custom_name || m.original_name,
        distance: m.start_m != null && m.end_m != null ? `${m.start_m}m - ${m.end_m}m` : `CH${m.dts_ch}-C${m.dts_code}`,
        temp: m.temp_avg,
        temp_avg: m.temp_avg,
        temp_min: m.temp_min,
        temp_max: m.temp_max,
        temp_min_p: m.temp_min_p,
        temp_max_p: m.temp_max_p,
        isAlarm: alarms.some(a => a.is_active && a.ch === m.dts_ch && a.code === m.dts_code), 
        status: alarms.some(a => a.is_active && a.ch === m.dts_ch && a.code === m.dts_code) ? 'Alarm' : 'Normal',
        mainGroup: m.main_group,
        subGroup: m.sub_group,"""

new_base_areas = """  const baseAreas: (SegmentData & { mainGroup: string; subGroup: string | null })[] = mappings.map(m => {
      const isCableBroken = m.temp_max < -50;
      const isTempCritical = m.temp_max >= criticalThreshold;
      const isTempWarning = m.temp_max >= warningThreshold;
      const isDbAlarm = alarms.some(a => a.is_active && a.ch === m.dts_ch && a.code === m.dts_code);
      
      const isAlarm = isCableBroken || isTempCritical || isDbAlarm;
      let status = 'Normal';
      if (isCableBroken) status = 'Broken Cable';
      else if (isTempCritical) status = 'Critical';
      else if (isTempWarning) status = 'Warning';
      else if (isDbAlarm) status = 'Alarm';
      
      return {
        id: m.id,
        name: m.custom_name || m.original_name,
        distance: m.start_m != null && m.end_m != null ? `${m.start_m}m - ${m.end_m}m` : `CH${m.dts_ch}-C${m.dts_code}`,
        temp: m.temp_max, // Changed to display max temperature
        temp_avg: m.temp_avg,
        temp_min: m.temp_min,
        temp_max: m.temp_max,
        temp_min_p: m.temp_min_p,
        temp_max_p: m.temp_max_p,
        isAlarm, 
        status,
        mainGroup: m.main_group,
        subGroup: m.sub_group,"""

db = db.replace(old_base_areas, new_base_areas)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(db)

