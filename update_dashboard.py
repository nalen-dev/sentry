import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    code = f.read()

# Pass props to DiagramVisualization
old_tag = "<DiagramVisualization isFullscreen={isFullscreen} />"
new_tag = "<DiagramVisualization isFullscreen={isFullscreen} segments={mappings} warningThreshold={warningThreshold} criticalThreshold={criticalThreshold} />"

code = code.replace(old_tag, new_tag)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(code)

