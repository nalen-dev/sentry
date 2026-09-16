import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# Remove the stray line
code = re.sub(r'\s*<path d="M 493,330 L 493,360"[^>]*/>\n', '\n', code)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

