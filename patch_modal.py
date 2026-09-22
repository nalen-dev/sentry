import re

with open('src/components/SegmentDetailModal.tsx', 'r') as f:
    content = f.read()

# Add imports
content = content.replace("import { LineChart as RechartsLineChart", "import DiagramVisualization from '../features/map/DiagramVisualization';\nimport { LineChart as RechartsLineChart")
content = content.replace("import { X, Save, Activity, MapPin, AlignLeft, Info, Thermometer, AlertTriangle, Check, Edit2 } from 'lucide-react';", "import { X, Save, Activity, MapPin, AlignLeft, Info, Thermometer, AlertTriangle, Check, Edit2, Layout } from 'lucide-react';")

# Add state
state_old = "const [chartData, setChartData] = useState<any[]>([]);"
state_new = "const [chartData, setChartData] = useState<any[]>([]);\n  const [activeTab, setActiveTab] = useState<'chart' | 'pid'>('chart');"
content = content.replace(state_old, state_new)

# Replace the Chart section
chart_old = """            {/* Chart */}
            <div className="h-1/2 flex flex-col bg-bg-base border border-border rounded-xl p-5 shadow-inner">
              <div className="flex justify-between items-center mb-4">
                <span className="text-xs font-bold text-text-primary uppercase tracking-widest flex items-center"><Activity size={16} className="mr-2 text-scada-primary" /> Temperature vs Time (30m)</span>
              </div>
              
              <div className="flex-1 w-full min-h-0">
                 <ResponsiveContainer width="100%" height="100%">
                   <RechartsLineChart data={chartData} margin={{ top: 5, right: 20, left: -20, bottom: 0 }}>
                     <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" opacity={0.3} />
                     <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} tickMargin={10} />
                     <YAxis stroke="#9ca3af" fontSize={12} domain={[0, 100]} />
                     <RechartsTooltip 
                       contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', fontSize: '12px' }}
                       itemStyle={{ color: '#43b581' }}
                     />
                     <Line type="monotone" dataKey="temp" stroke="#43b581" strokeWidth={2} dot={false} activeDot={{ r: 6, fill: '#43b581' }} connectNulls={true} />
                   </RechartsLineChart>
                 </ResponsiveContainer>
              </div>
            </div>"""

chart_new = """            {/* View Mode Toggle & Content */}
            <div className="h-[55%] flex flex-col bg-bg-base border border-border rounded-xl p-0 shadow-inner overflow-hidden">
              <div className="flex border-b border-border bg-bg-surface">
                <button 
                  onClick={() => setActiveTab('chart')} 
                  className={`flex-1 py-3 text-xs font-bold tracking-widest flex items-center justify-center transition-colors ${activeTab === 'chart' ? 'bg-bg-base text-scada-primary border-b-2 border-scada-primary' : 'text-text-secondary hover:text-text-primary'}`}
                >
                  <Activity size={16} className="mr-2" /> RIWAYAT SUHU (30m)
                </button>
                <button 
                  onClick={() => setActiveTab('pid')} 
                  className={`flex-1 py-3 text-xs font-bold tracking-widest flex items-center justify-center transition-colors ${activeTab === 'pid' ? 'bg-bg-base text-scada-primary border-b-2 border-scada-primary' : 'text-text-secondary hover:text-text-primary'}`}
                >
                  <Layout size={16} className="mr-2" /> P&ID DIAGRAM
                </button>
              </div>
              
              <div className="flex-1 w-full min-h-0 relative p-4">
                {activeTab === 'chart' ? (
                   <ResponsiveContainer width="100%" height="100%">
                     <RechartsLineChart data={chartData} margin={{ top: 5, right: 20, left: -20, bottom: 0 }}>
                       <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" opacity={0.3} />
                       <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} tickMargin={10} />
                       <YAxis stroke="#9ca3af" fontSize={12} domain={[0, 100]} />
                       <RechartsTooltip 
                         contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', fontSize: '12px' }}
                         itemStyle={{ color: '#43b581' }}
                       />
                       <Line type="monotone" dataKey="temp" stroke="#43b581" strokeWidth={2} dot={false} activeDot={{ r: 6, fill: '#43b581' }} connectNulls={true} />
                     </RechartsLineChart>
                   </ResponsiveContainer>
                ) : (
                   <div className="absolute inset-0">
                     <DiagramVisualization 
                        isFullscreen={true} 
                        hideHeader={true}
                        alwaysShowPin={true}
                        warningThreshold={45}
                        criticalThreshold={60}
                        segments={[{
                          main_group: segment.mainGroup || '',
                          sub_group: segment.subGroup || null,
                          start_m: segment.start_m,
                          end_m: segment.end_m,
                          temp_max: segment.temp_max ?? segment.temp,
                          temp_avg: segment.temp_avg ?? segment.temp,
                        }]}
                     />
                   </div>
                )}
              </div>
            </div>"""

content = content.replace(chart_old, chart_new)

# Adjust height of right column inner components to look better
content = content.replace('className="flex-1 flex flex-col bg-bg-base border border-border rounded-xl p-5 shadow-inner min-h-0"', 'className="h-[45%] flex flex-col bg-bg-base border border-border rounded-xl p-5 shadow-inner min-h-0"')

with open('src/components/SegmentDetailModal.tsx', 'w') as f:
    f.write(content)

