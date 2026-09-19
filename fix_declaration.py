import re

with open('src/pages/LogsPage.tsx', 'r') as f:
    code = f.read()

code = code.replace("const [filterType, setFilterType] = useState<'all' | 'info' | 'warn' | 'error'>('all');\n  const [selectedDate, setSelectedDate] = useState<string>('');", "const [filterType, setFilterType] = useState<'all' | 'info' | 'warn' | 'error'>('all');")

code = code.replace("const [logs, setLogs] = useState<SystemLog[]>([]);", "const [logs, setLogs] = useState<SystemLog[]>([]);\n  const [selectedDate, setSelectedDate] = useState<string>('');")

with open('src/pages/LogsPage.tsx', 'w') as f:
    f.write(code)

