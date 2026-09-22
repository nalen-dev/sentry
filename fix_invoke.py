import re

with open('src-tauri/src/lib.rs', 'r') as f:
    content = f.read()

content = content.replace("get_map_calibration,", "get_map_calibration,\n            write_system_log,\n            get_system_logs,")
content = content.replace("save_map_calibration\n        ])", "save_map_calibration,\n            write_system_log,\n            get_system_logs\n        ])")

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(content)

