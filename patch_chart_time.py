import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    code = f.read()

# Replace the state
old_state = "const [selectedTimeRange, setSelectedTimeRange] = useState('30m');"
new_state = "const [timeRangeDays, setTimeRangeDays] = useState(0);\n  const [timeRangeHours, setTimeRangeHours] = useState(1);"
code = code.replace(old_state, new_state)

# Replace the effect dependencies
code = code.replace("}, [selectedTimeRange, chartMode, selectedGroup, mappings]);", "}, [timeRangeDays, timeRangeHours, chartMode, selectedGroup, mappings]);")

# Replace minutes calculation
old_calc = "const minutes = selectedTimeRange === '30m' ? 30 : selectedTimeRange === '1h' ? 60 : selectedTimeRange === '6h' ? 360 : 30;"
new_calc = "const minutes = (timeRangeDays * 24 * 60) + (timeRangeHours * 60);"
code = code.replace(old_calc, new_calc)

# Replace UI
old_ui = """<div className="flex bg-bg-panel border border-border rounded-lg overflow-hidden shadow-sm">
                {['30m', '1h', '6h'].map(range => (
                  <button
                    key={range}
                    onClick={() => setSelectedTimeRange(range)}
                    className={`px-4 py-2 font-mono text-sm font-bold transition-colors ${
                      selectedTimeRange === range 
                        ? 'bg-scada-primary/20 text-scada-primary border-b-2 border-scada-primary' 
                        : 'text-text-secondary hover:bg-bg-surface hover:text-text-primary border-b-2 border-transparent'
                    }`}
                  >
                    {range}
                  </button>
                ))}
              </div>"""

new_ui = """<div className="flex bg-bg-panel border border-border rounded-lg overflow-hidden shadow-sm items-center px-2 py-1 space-x-2">
                <span className="text-xs font-bold text-text-secondary">RANGE:</span>
                <input type="number" min="0" max="30" value={timeRangeDays} onChange={e => setTimeRangeDays(parseInt(e.target.value) || 0)} className="w-16 bg-bg-surface border border-border rounded px-2 py-1 text-xs text-text-primary outline-none" title="Days" />
                <span className="text-xs font-mono text-text-secondary">Days</span>
                <input type="number" min="0" max="23" value={timeRangeHours} onChange={e => setTimeRangeHours(parseInt(e.target.value) || 0)} className="w-16 bg-bg-surface border border-border rounded px-2 py-1 text-xs text-text-primary outline-none" title="Hours" />
                <span className="text-xs font-mono text-text-secondary">Hours</span>
              </div>"""

code = code.replace(old_ui, new_ui)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(code)

