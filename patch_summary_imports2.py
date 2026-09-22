import re

with open('src-tauri/src/lib.rs', 'r') as f:
    content = f.read()

content = content.replace("get_settings(state.clone())", "get_all_settings(state.clone())")

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(content)

