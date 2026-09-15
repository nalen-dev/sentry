import re

with open('src/features/dashboard/DataModal.tsx', 'r') as f:
    dm = f.read()

dm = dm.replace(
    'tracking-wider border-b border-border">Avg Temp</th>',
    'tracking-wider border-b border-border">Max Temp</th>'
)

with open('src/features/dashboard/DataModal.tsx', 'w') as f:
    f.write(dm)

