import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    content = f.read()

target = r'\{loading && chartData\.length === 0 \? \(\n\s*<div className="flex-1 flex items-center justify-center font-mono text-text-secondary animate-pulse">LOADING HISTORICAL DATA\.\.\.</div>\n\s*\) : \('

replacement = """{loading && chartData.length === 0 ? (
            <div className="flex-1 flex items-center justify-center font-mono text-scada-primary animate-pulse tracking-widest font-bold">LOADING HISTORICAL DATA...</div>
          ) : (!loading && chartData.length === 0) ? (
            <div className="flex-1 flex items-center justify-center font-mono text-red-400 tracking-widest font-bold text-center">
              NO SEGMENTS FOUND.<br/>PLEASE SYNC FROM DTS IN SETTINGS.
            </div>
          ) : ("""

content = re.sub(target, replacement, content)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(content)
