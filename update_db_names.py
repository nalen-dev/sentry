import re

with open('src-tauri/src/db.rs', 'r') as f:
    code = f.read()

code = code.replace("FIBER A (TN BEK 5-6)", "BEK56")
code = code.replace("FIBER B (TN BEK 3-4)", "BEK34")
code = code.replace("FIBER D (TN TCM 1-6)", "TCM16")
code = code.replace("BC4B-BC5 TRANSITION", "BC45-MOTOR")

with open('src-tauri/src/db.rs', 'w') as f:
    f.write(code)

