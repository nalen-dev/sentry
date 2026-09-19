import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    code = f.read()

# Replace AreaChart block
start_idx = code.find("<AreaChart")
end_idx = code.find("</AreaChart>") + len("</AreaChart>")

old_block = code[start_idx:end_idx]

new_block = """
              {(() => {
                const dynamicColor = stats.max >= 60 ? '#ef4444' : (stats.max >= 45 ? '#eab308' : '#10b981');
                return (
                  <AreaChart data={spatialData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={dynamicColor} stopOpacity={0.8}/>
                        <stop offset="95%" stopColor={dynamicColor} stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" opacity={0.3} vertical={false} />
                    <XAxis dataKey="distance" stroke="#9ca3af" fontSize={12} tickMargin={10} tickFormatter={(v) => `${v}m`} />
                    <YAxis stroke="#9ca3af" fontSize={12} domain={[0, 100]} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', fontSize: '12px' }}
                      itemStyle={{ color: dynamicColor, fontWeight: 'bold' }}
                      labelStyle={{ color: 'var(--text-secondary)' }}
                      labelFormatter={(v) => `Distance: ${v} meters`}
                    />
                    
                    <ReferenceLine y={45} stroke="#eab308" strokeDasharray="5 5" label={{ position: 'insideTopLeft', value: 'WARNING THRESHOLD', fill: '#eab308', fontSize: 10, fontWeight: 'bold' }} />
                    <ReferenceLine y={60} stroke="#ef4444" strokeDasharray="5 5" label={{ position: 'insideTopLeft', value: 'DANGER THRESHOLD', fill: '#ef4444', fontSize: 10, fontWeight: 'bold' }} />
                    
                    <Area type="monotone" dataKey="temp" name="Temperature (°C)" stroke={dynamicColor} strokeWidth={2} fillOpacity={1} fill="url(#colorTemp)" />
                  </AreaChart>
                );
              })()}
""".strip()

code = code[:start_idx] + new_block + code[end_idx:]

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(code)

