import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    code = f.read()

# Add states
state_injection = """  const [selectedGroup, setSelectedGroup] = useState<string>('');
  const [warningThreshold, setWarningThreshold] = useState(45);
  const [criticalThreshold, setCriticalThreshold] = useState(60);"""

code = code.replace("  const [selectedGroup, setSelectedGroup] = useState<string>('');", state_injection)

# Add get_all_settings to useEffect
useEffect_injection = """
  // Load Thresholds
  useEffect(() => {
    invoke<Record<string, string>>('get_all_settings').then(settings => {
      if (settings['warning_threshold']) setWarningThreshold(Number(settings['warning_threshold']));
      if (settings['critical_threshold']) setCriticalThreshold(Number(settings['critical_threshold']));
    }).catch(console.error);
  }, []);

  // Spatial Data Update"""

code = code.replace("  // Spatial Data Update", useEffect_injection)

# Fix Reference Lines and Colors
dynamic_color_fix = """const dynamicColor = stats.max >= criticalThreshold ? '#ef4444' : (stats.max >= warningThreshold ? '#eab308' : '#10b981');"""
code = code.replace("const dynamicColor = stats.max >= 60 ? '#ef4444' : (stats.max >= 45 ? '#eab308' : '#10b981');", dynamic_color_fix)

code = code.replace("<ReferenceLine y={45} stroke=\"#eab308\" strokeDasharray=\"5 5\" label={{ position: 'insideTopLeft', value: 'WARNING THRESHOLD', fill: '#eab308', fontSize: 10, fontWeight: 'bold' }} />", "<ReferenceLine y={warningThreshold} stroke=\"#eab308\" strokeDasharray=\"5 5\" label={{ position: 'insideTopLeft', value: 'WARNING THRESHOLD', fill: '#eab308', fontSize: 10, fontWeight: 'bold' }} />")
code = code.replace("<ReferenceLine y={60} stroke=\"#ef4444\" strokeDasharray=\"5 5\" label={{ position: 'insideTopLeft', value: 'DANGER THRESHOLD', fill: '#ef4444', fontSize: 10, fontWeight: 'bold' }} />", "<ReferenceLine y={criticalThreshold} stroke=\"#ef4444\" strokeDasharray=\"5 5\" label={{ position: 'insideTopLeft', value: 'DANGER THRESHOLD', fill: '#ef4444', fontSize: 10, fontWeight: 'bold' }} />")


with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(code)

