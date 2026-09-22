import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    content = f.read()

# Add state for summary
state_old = "const [chartMode, setChartMode] = useState<ChartMode>('history');"
state_new = "const [chartMode, setChartMode] = useState<ChartMode>('history');\n  const [histSummary, setHistSummary] = useState<any>(null);"
content = content.replace(state_old, state_new)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(content)

