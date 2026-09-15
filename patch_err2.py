import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    'CONNECTION ERROR.<br/>RETRYING...',
    'CONNECTION ERROR.<br/>RETRYING...<br/><span className="text-xs text-red-400 mt-2 block">{errorMessage}</span>'
)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(content)

