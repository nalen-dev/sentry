import re

with open('src-tauri/src/lib.rs', 'r') as f:
    code = f.read()

# Fix the function definition
bad_def = """async fn test_db_connection,
            get_map_calibration,
            save_map_calibration("""

good_def = "async fn test_db_connection("

code = code.replace(bad_def, good_def)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(code)

