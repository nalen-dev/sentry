import re

with open('src-tauri/src/lib.rs', 'r') as f:
    lib = f.read()

broken_block = """        for r in rows {
            if let Some(ct) = r.CreationTime {
                if ct < cutoff_time { continue; }

            if let Some(ct) = r.CreationTime {"""

fixed_block = """        for r in rows {
            if let Some(ct) = r.CreationTime {
                if ct < cutoff_time { continue; }"""

lib = lib.replace(broken_block, fixed_block)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(lib)

