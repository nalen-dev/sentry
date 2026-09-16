import re

with open('src/pages/SettingPage.tsx', 'r') as f:
    code = f.read()

# Add Map to imports
code = code.replace("  Link2\n} from 'lucide-react';", "  Link2,\n  Map\n} from 'lucide-react';")

# Add map-calibration to tabs array
old_tabs = """  const tabs = [
    { id: 'time', label: 'Time & Date', icon: Clock },
    { id: 'mapping', label: 'Segment Mapping', icon: Link2 },
    { id: 'users', label: 'User Management', icon: Users },
    { id: 'database', label: 'Database Connection', icon: Database },
    { id: 'threshold', label: 'Alarm Thresholds', icon: Thermometer },
    { id: 'advanced', label: 'Advanced Settings', icon: ShieldAlert },
  ];"""

new_tabs = """  const tabs = [
    { id: 'time', label: 'Time & Date', icon: Clock },
    { id: 'mapping', label: 'Segment Mapping', icon: Link2 },
    { id: 'map-calibration', label: 'Map Calibration', icon: Map },
    { id: 'users', label: 'User Management', icon: Users },
    { id: 'database', label: 'Database Connection', icon: Database },
    { id: 'threshold', label: 'Alarm Thresholds', icon: Thermometer },
    { id: 'advanced', label: 'Advanced Settings', icon: ShieldAlert },
  ];"""

code = code.replace(old_tabs, new_tabs)

with open('src/pages/SettingPage.tsx', 'w') as f:
    f.write(code)

