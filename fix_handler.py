import re

with open('src-tauri/src/lib.rs', 'r') as f:
    code = f.read()

# Replace the handler
old_handler = "            get_app_settings,\n            save_app_setting,"
new_handler = "            get_app_settings,\n            save_app_setting,\n            get_map_calibration,\n            save_map_calibration,"

if new_handler not in code:
    code = code.replace(old_handler, new_handler)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(code)

