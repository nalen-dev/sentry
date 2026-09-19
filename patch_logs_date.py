import re

with open('src/pages/LogsPage.tsx', 'r') as f:
    code = f.read()

# Add selectedDate state
code = code.replace("const [filterType, setFilterType] = useState<string>('all');", "const [filterType, setFilterType] = useState<string>('all');\n  const [selectedDate, setSelectedDate] = useState<string>('');")

# Update get_alarms invoke
old_invoke = "const alarms: any[] = await invoke('get_alarms');"
new_invoke = "const dateParam = selectedDate ? selectedDate : null;\n        const alarms: any[] = await invoke('get_alarms', { date: dateParam });"
code = code.replace(old_invoke, new_invoke)

# Add selectedDate to useEffect deps
old_dep = "}, []);"
new_dep = "}, [selectedDate]);"
code = code.replace(old_dep, new_dep)

# Replace UI
old_ui = '<button className="flex items-center px-4 py-2 bg-bg-panel border border-border rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-surface transition-colors font-bold text-sm shadow-sm">\n              <Calendar size={16} className="mr-2" /> SELECT DATE RANGE\n            </button>'

new_ui = '<input type="date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)} className="flex items-center px-4 py-2 bg-bg-panel border border-border rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-surface transition-colors font-bold text-sm shadow-sm outline-none" />'
code = code.replace(old_ui, new_ui)

with open('src/pages/LogsPage.tsx', 'w') as f:
    f.write(code)

