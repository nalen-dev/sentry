import re

with open('src/features/dashboard/RightPanel.tsx', 'r') as f:
    rp = f.read()

# Replace states and fetch logic
old_fetch = r"  const \[chartMode, setChartMode\] = useState\<'area' \| 'history'\>\('area'\);\n  const \[historyData, setHistoryData\] = useState\<any\[\]\>\(\[\]\);\n  \n  \/\/ Fetch history for the hottest segment if in history mode\n  useEffect\(\(\) => \{\n    let isMounted = true;\n    import\('@tauri-apps/api/core'\)\.then\(\(\{ invoke \}\) => \{\n      const fetchHistory = async \(\) => \{\n        if \(chartMode !== 'history' \|\| filteredAreas\.length === 0\) return;\n        \n        \/\/ Find hottest segment\n        const hottest = \[\.\.\.filteredAreas\]\.sort\(\(a, b\) => \(b\.temp_avg \|\| 0\) - \(a\.temp_avg \|\| 0\)\)\[0\];\n        if \(\!hottest \|\| \!hottest\.dts_ch \|\| \!hottest\.dts_code\) return;\n        \n        try \{\n          const data = await invoke\<any\[\]\>\('get_segment_history', \{ dtsCh: hottest\.dts_ch, dtsCode: hottest\.dts_code, limit: 30 \}\);\n          if \(isMounted\) setHistoryData\(data\);\n        \} catch \(err\) \{\n          console\.error\(\"Failed to fetch history for RightPanel\", err\);\n        \}\n      \};\n      \n      fetchHistory\(\);\n      const timer = setInterval\(fetchHistory, 5000\);\n      return \(\) => \{ isMounted = false; clearInterval\(timer\); \};\n    \}\);\n  \}, \[chartMode, filteredAreas\]\);"

new_fetch = """  const [chartMode, setChartMode] = useState<'area' | 'history'>('area');
  const [historyData, setHistoryData] = useState<any[]>([]);
  const [histGroups, setHistGroups] = useState<string[]>([]);
  
  // Fetch group history (like Chart Menu)
  useEffect(() => {
    let isMounted = true;
    import('@tauri-apps/api/core').then(({ invoke }) => {
      const fetchHistory = async () => {
        if (chartMode !== 'history') return;
        
        try {
          const data: any[] = await invoke('get_groups_history', { minutes: 30 });
          if (!isMounted) return;
          
          if (data.length === 0) {
            setHistoryData([]);
            return;
          }
          
          const groupsSet = new Set<string>();
          const flatData = data.map(pt => {
            const row: any = { time: pt.time };
            for (const [g, val] of Object.entries(pt.groups)) {
              row[g] = val;
              groupsSet.add(g);
            }
            return row;
          });
          
          setHistGroups(Array.from(groupsSet).sort());
          setHistoryData(flatData);
        } catch (err) {
          console.error("Failed to fetch group history for RightPanel", err);
        }
      };
      
      fetchHistory();
      const timer = setInterval(fetchHistory, 10000);
      return () => { isMounted = false; clearInterval(timer); };
    });
  }, [chartMode]);"""

rp = re.sub(old_fetch, new_fetch, rp)

# Replace the Recharts JSX
old_jsx = r"<XAxis dataKey=\{chartMode === 'area' \? \"name\" : \"time\"\} stroke=\"#9ca3af\" fontSize=\{10\} tickMargin=\{5\} \/>\n              <YAxis stroke=\"#9ca3af\" fontSize=\{10\} \/>\n              <Tooltip \n                contentStyle=\{\{ backgroundColor: 'var\(--bg-panel\)', borderColor: 'var\(--border-color\)', borderRadius: '8px', fontSize: '12px' \}\}\n                itemStyle=\{\{ color: 'var\(--scada-primary\)', fontWeight: 'bold' \}\}\n                labelStyle=\{\{ color: 'var\(--text-secondary\)' \}\}\n                formatter=\{\(value: any, _name: any, props: any\) => \{\n                  return \[`\$\{value\}°C`, chartMode === 'area' \? `Area: \$\{props\.payload\.name\}` : `Temp`\];\n                \}\}\n              \/>\n              <Line type=\"monotone\" dataKey=\"temp\" stroke=\"var\(--scada-primary\)\" strokeWidth=\{2\} dot=\{chartMode === 'area' \? \{ r: 3, fill: 'var\(--scada-primary\)', strokeWidth: 0 \} : false\} activeDot=\{\{ r: 5, strokeWidth: 0 \}\} \/>"

new_jsx = """<XAxis dataKey={chartMode === 'area' ? "name" : "time"} stroke="#9ca3af" fontSize={10} tickMargin={5} />
              <YAxis stroke="#9ca3af" fontSize={10} />
              <Tooltip 
                contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', fontSize: '12px' }}
                itemStyle={{ fontWeight: 'bold' }}
                labelStyle={{ color: 'var(--text-secondary)' }}
              />
              {chartMode === 'area' ? (
                <Line type="monotone" dataKey="temp" name="Temperature" stroke="var(--scada-primary)" strokeWidth={2} dot={{ r: 3, fill: 'var(--scada-primary)', strokeWidth: 0 }} activeDot={{ r: 5, strokeWidth: 0 }} />
              ) : (
                histGroups.map((name, i) => (
                  <Line key={name} type="monotone" dataKey={name} name={name} stroke={['#06b6d4', '#eab308', '#ef4444', '#10b981', '#a855f7', '#f97316'][i % 6]} strokeWidth={2} dot={false} activeDot={{ r: 4, strokeWidth: 0 }} />
                ))
              )}"""

rp = re.sub(old_jsx, new_jsx, rp)

# change toggle button text
rp = rp.replace("HISTORY (HOTTEST)", "GROUP HISTORY (30M)")

with open('src/features/dashboard/RightPanel.tsx', 'w') as f:
    f.write(rp)

