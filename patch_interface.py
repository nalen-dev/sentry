import re

with open('src/components/SegmentDetailModal.tsx', 'r') as f:
    code = f.read()

code = code.replace("group?: string;", "group?: string;\n  mainGroup?: string;\n  subGroup?: string;")

with open('src/components/SegmentDetailModal.tsx', 'w') as f:
    f.write(code)

