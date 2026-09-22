import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

old_name = "const name = seg.custom_name || seg.original_name;"
new_name = "const name = (seg as any).smart_name || seg.custom_name || seg.original_name;"

content = content.replace(old_name, new_name)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)

