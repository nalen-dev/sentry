import re

with open('src/pages/LogsPage.tsx', 'r') as f:
    code = f.read()

# Fix LogsPage
code = code.replace("const [filterType, setFilterType] = useState<'all' | 'info' | 'warn' | 'error'>('all');", "const [filterType, setFilterType] = useState<'all' | 'info' | 'warn' | 'error'>('all');\n  const [selectedDate, setSelectedDate] = useState<string>('');")

with open('src/pages/LogsPage.tsx', 'w') as f:
    f.write(code)

with open('src/pages/ChartPage.tsx', 'r') as f:
    code = f.read()

# Fix ChartPage timeRangeDays left over
code = code.replace("timeRangeDays", "selectedDate")

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(code)

