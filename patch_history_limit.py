import re

with open('src-tauri/src/lib.rs', 'r') as f:
    content = f.read()

content = content.replace("let limit = minutes * 10;", "let limit = minutes * 60;")

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(content)

