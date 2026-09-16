import re

with open('src-tauri/src/lib.rs', 'r') as f:
    code = f.read()

# Replace the handler
old_handler = "test_db_connection"
new_handler = "test_db_connection,\n            get_map_calibration,\n            save_map_calibration"

code = code.replace(old_handler, new_handler)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(code)

