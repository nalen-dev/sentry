import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    code = f.read()

code = code.replace("domain={['dataMin - 2', 'dataMax + 5']}", "domain={[0, 100]}")

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(code)

