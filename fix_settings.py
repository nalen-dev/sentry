import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    db = f.read()

# Add a useEffect for fetching settings once
new_effect = """  useEffect(() => {
    import('@tauri-apps/api/core').then(({ invoke }) => {
      invoke<Record<string, string>>('get_all_settings').then(settings => {
        if (settings['warning_threshold']) setWarningThreshold(Number(settings['warning_threshold']));
        if (settings['critical_threshold']) setCriticalThreshold(Number(settings['critical_threshold']));
      }).catch(console.error);
    });
  }, []);"""

db = db.replace(
    "useEffect(() => {",
    new_effect + "\n\n  useEffect(() => {",
    1
)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(db)

