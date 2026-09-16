import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# Remove Top Nodes
code = re.sub(r'\{/\* Top Nodes.*?\}\)\)}', '', code, flags=re.DOTALL)

# Remove Bottom Nodes
code = re.sub(r'\{/\* Bottom Nodes.*?\}\)\)}', '', code, flags=re.DOTALL)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

