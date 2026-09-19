import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    code = f.read()

# Replace states
code = code.replace("const [timeRangeDays, setTimeRangeDays] = useState(0);", "const [selectedDate, setSelectedDate] = useState<string>('');")
code = code.replace("const [timeRangeHours, setTimeRangeHours] = useState(1);", "const [timeRangeHours, setTimeRangeHours] = useState(24);")

# Replace minutes calculation
old_calc = "const minutes = (timeRangeDays * 24 * 60) + (timeRangeHours * 60);"
new_calc = "const minutes = timeRangeHours * 60;"
code = code.replace(old_calc, new_calc)

# Add date parameter to get_groups_history
old_invoke = "const history: any[] = await invoke('get_groups_history', { minutes });"
new_invoke = "const dateParam = selectedDate ? selectedDate : null;\n          const history: any[] = await invoke('get_groups_history', { minutes, date: dateParam });"
code = code.replace(old_invoke, new_invoke)

# Add selectedDate to useEffect dependency
old_dep = "}, [chartMode, timeRangeDays, timeRangeHours, selectedGroup]);"
new_dep = "}, [chartMode, selectedDate, timeRangeHours, selectedGroup]);"
code = code.replace(old_dep, new_dep)

# Replace UI
old_ui = """<span className="text-xs font-bold text-text-secondary">RANGE:</span>
                <input type="number" min="0" max="30" value={timeRangeDays} onChange={e => setTimeRangeDays(parseInt(e.target.value) || 0)} className="w-16 bg-bg-surface border border-border rounded px-2 py-1 text-xs text-text-primary outline-none" title="Days" />
                <span className="text-xs font-mono text-text-secondary">Days</span>
                <input type="number" min="0" max="23" value={timeRangeHours} onChange={e => setTimeRangeHours(parseInt(e.target.value) || 0)} className="w-16 bg-bg-surface border border-border rounded px-2 py-1 text-xs text-text-primary outline-none" title="Hours" />
                <span className="text-xs font-mono text-text-secondary">Hours</span>"""

new_ui = """<span className="text-xs font-bold text-text-secondary">DATE:</span>
                <input type="date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)} className="bg-bg-surface border border-border rounded px-2 py-1 text-xs text-text-primary outline-none" />
                <span className="text-xs font-bold text-text-secondary ml-2">RANGE:</span>
                <input type="number" min="1" max="24" value={timeRangeHours} onChange={e => setTimeRangeHours(parseInt(e.target.value) || 1)} className="w-16 bg-bg-surface border border-border rounded px-2 py-1 text-xs text-text-primary outline-none" title="Hours" />
                <span className="text-xs font-mono text-text-secondary">Hours</span>"""

code = code.replace(old_ui, new_ui)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(code)

