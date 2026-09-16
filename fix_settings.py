import re

with open('src/pages/SettingPage.tsx', 'r') as f:
    code = f.read()

# Fix SettingTab
code = code.replace("type SettingTab = 'time' | 'mapping' | 'users' | 'database' | 'threshold' | 'advanced';", "type SettingTab = 'time' | 'mapping' | 'map-calibration' | 'users' | 'database' | 'threshold' | 'advanced';")

# Insert MapCalibration interface before default export
interface_code = """
export interface MapCalibration {
  id?: number;
  main_group: string;
  start_m: number;
  end_m: number;
  start_svg_x: number;
  start_svg_y: number;
  end_svg_x: number;
  end_svg_y: number;
  start_lat?: number;
  start_lng?: number;
  end_lat?: number;
  end_lng?: number;
}

"""

code = code.replace("export default function SettingPage() {", interface_code + "export default function SettingPage() {")

with open('src/pages/SettingPage.tsx', 'w') as f:
    f.write(code)

