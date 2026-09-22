import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

# Add global variable outside component
if "const globalAlarmState" not in content:
    content = content.replace(
        "export default function Dashboard() {",
        "const globalAlarmState: Record<number, 'normal'|'warning'|'danger'> = {};\n\nexport default function Dashboard() {"
    )
    
# Remove unused useRef
content = content.replace("import { useState, useEffect, useRef}  from 'react';", "import { useState, useEffect }  from 'react';")

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)

