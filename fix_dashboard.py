import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

# Remove DUMMY_AREAS import
content = re.sub(r"import \{ DUMMY_AREAS\} from '\.\./data/constants';\n", "", content)

# Add isLoading to state
state_block = r"  const \[mappings, setMappings\] = useState<LiveSegment\[\]>\(\[\]\);\n  const \[alarms, setAlarms\] = useState<AlarmLog\[\]>\(\[\]\);"
new_state_block = """  const [mappings, setMappings] = useState<LiveSegment[]>([]);
  const [alarms, setAlarms] = useState<AlarmLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);"""
content = re.sub(state_block, new_state_block, content)

# Update fetchLive
fetch_old = r"      const fetchLive = \(\) => \{\n        import\('@tauri-apps/api/core'\)\.then\(\(\{ invoke \}\) => \{\n          invoke<LiveSegment\[\]>\('get_live_segments'\)\n            \.then\(setMappings\)\n            \.catch\(err => console\.error\(\"Failed to load live segments\", err\)\);\n            \n          invoke<AlarmLog\[\]>\('get_alarms'\)\n            \.then\(setAlarms\)\n            \.catch\(err => console\.error\(\"Failed to load alarms\", err\)\);\n        \}\);\n      \};"
fetch_new = """      const fetchLive = () => {
        import('@tauri-apps/api/core').then(({ invoke }) => {
          Promise.all([
            invoke<LiveSegment[]>('get_live_segments'),
            invoke<AlarmLog[]>('get_alarms')
          ]).then(([m, a]) => {
            setMappings(m);
            setAlarms(a);
            setIsLoading(false);
          }).catch(err => {
            console.error("Failed to load live data", err);
            setIsLoading(false);
          });
        });
      };"""
content = re.sub(fetch_old, fetch_new, content)

# Fix baseAreas calculation
base_areas_old = r"  const baseAreas: \(SegmentData & \{ mainGroup: string; subGroup: string \| null \}\)\[\] = mappings\.length > 0 \n    \? mappings\.map.*?undefined \}\)\);\n"
base_areas_new = """  const baseAreas: (SegmentData & { mainGroup: string; subGroup: string | null })[] = mappings.map(m => ({
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
        subGroup: m.sub_group,
        mappingId: m.id,
        original_name: m.original_name,
        dts_ch: m.dts_ch,
        dts_code: m.dts_code,
        start_m: m.start_m ?? undefined,
        end_m: m.end_m ?? undefined,
      }));\n"""
content = re.sub(base_areas_old, base_areas_new, content, flags=re.DOTALL)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)

