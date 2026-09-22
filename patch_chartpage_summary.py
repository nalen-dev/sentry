import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    content = f.read()

# 1. Add state for summary
state_old = "const [chartMode, setChartMode] = useState<'history' | 'spatial'>('history');"
state_new = "const [chartMode, setChartMode] = useState<'history' | 'spatial'>('history');\n  const [histSummary, setHistSummary] = useState<any>(null);"
content = content.replace(state_old, state_new)

# 2. Fetch the summary
fetch_old = """          const [data, mappingsData] = await Promise.all([
             invoke<any[]>('get_groups_history', { startDt, endDt }),
             invoke<any[]>('get_segment_mappings')
          ]);"""
fetch_new = """          const [data, mappingsData, summary] = await Promise.all([
             invoke<any[]>('get_groups_history', { startDt, endDt }),
             invoke<any[]>('get_segment_mappings'),
             invoke<any>('get_history_summary', { startDt, endDt }).catch(e => { console.error(e); return null; })
          ]);
          setHistSummary(summary);"""
content = content.replace(fetch_old, fetch_new)

# 3. Add UI above chart + fix YAxis to 0-100
ui_old = """            chartMode === 'history' ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={histData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={isDarkMode ? '#333' : '#eee'} vertical={false} />
                  <XAxis dataKey="time" stroke={isDarkMode ? '#888' : '#666'} tick={{ fill: isDarkMode ? '#888' : '#666' }} />
                  <YAxis stroke={isDarkMode ? '#888' : '#666'} tick={{ fill: isDarkMode ? '#888' : '#666' }} domain={['auto', 'auto']} />"""

ui_new = """            chartMode === 'history' ? (
              <div className="flex flex-col h-full">
                {histSummary && (
                  <div className="flex gap-4 mb-4 shrink-0 overflow-x-auto">
                    <div className="bg-bg-surface border border-red-500/30 p-3 rounded-lg flex-1 min-w-[200px] flex items-center shadow-[0_0_15px_rgba(239,68,68,0.1)]">
                      <Thermometer className="text-red-500 mr-3 shrink-0" size={24} />
                      <div>
                        <div className="text-xs text-text-secondary font-bold tracking-wider">HIGHEST TEMP</div>
                        <div className="text-red-500 font-bold text-lg">{histSummary.max_temp.toFixed(1)}°C <span className="text-sm font-normal text-text-secondary">at {histSummary.max_time}</span></div>
                        <div className="text-xs font-mono text-text-secondary truncate" title={histSummary.max_segment}>{histSummary.max_group} - {histSummary.max_segment}</div>
                      </div>
                    </div>
                    <div className="bg-bg-surface border border-blue-500/30 p-3 rounded-lg flex-1 min-w-[200px] flex items-center shadow-[0_0_15px_rgba(59,130,246,0.1)]">
                      <Thermometer className="text-blue-500 mr-3 shrink-0" size={24} />
                      <div>
                        <div className="text-xs text-text-secondary font-bold tracking-wider">LOWEST TEMP</div>
                        <div className="text-blue-500 font-bold text-lg">{histSummary.min_temp.toFixed(1)}°C <span className="text-sm font-normal text-text-secondary">at {histSummary.min_time}</span></div>
                        <div className="text-xs font-mono text-text-secondary truncate" title={histSummary.min_segment}>{histSummary.min_group} - {histSummary.min_segment}</div>
                      </div>
                    </div>
                  </div>
                )}
                <div className="flex-1 min-h-0">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={histData} margin={{ top: 10, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke={isDarkMode ? '#333' : '#eee'} vertical={false} />
                      <XAxis dataKey="time" stroke={isDarkMode ? '#888' : '#666'} tick={{ fill: isDarkMode ? '#888' : '#666' }} />
                      <YAxis stroke={isDarkMode ? '#888' : '#666'} tick={{ fill: isDarkMode ? '#888' : '#666' }} domain={[0, 100]} />"""

content = content.replace(ui_old, ui_new)

# 4. Close the div correctly at the bottom of History chart
close_old = """                </LineChart>
              </ResponsiveContainer>
            ) : ("""

close_new = """                </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            ) : ("""
content = content.replace(close_old, close_new)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(content)

