import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    code = f.read()

# Add import
code = code.replace("import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine, AreaChart, Area } from 'recharts';", "import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceLine, AreaChart, Area } from 'recharts';\nimport { exportElementToPDF } from '../utils/exportPdf';")

# Add id to main container
code = code.replace('<div className="w-full h-full bg-bg-panel flex flex-col relative overflow-hidden custom-scrollbar p-6">', '<div id="chart-export-container" className="w-full h-full bg-bg-panel flex flex-col relative overflow-hidden custom-scrollbar p-6">')

# Replace Export CSV button
old_export = """<button onClick={handleExportCsv} className="flex items-center px-4 py-2 bg-bg-panel border border-border rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-surface transition-colors font-bold text-sm shadow-sm">
              <Download size={16} className="mr-2" /> EXPORT CSV
            </button>"""
new_export = """<button onClick={() => exportElementToPDF('chart-export-container', `DTS_Chart_${chartMode}_${new Date().getTime()}`)} className="flex items-center px-4 py-2 bg-bg-panel border border-border rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-surface transition-colors font-bold text-sm shadow-sm">
              <Download size={16} className="mr-2" /> EXPORT PDF
            </button>"""

code = code.replace(old_export, new_export)

# Replace the dynamic date filter logic in ChartPage
# Task 2: "buat agar lebih dinamis, bisa menentukan hingga hari dan jam nya."
# Currently ChartPage uses `selectedTimeRange` ('30m', '1h', '6h'). We need to replace it with a robust date/time picker or a custom dropdown that allows "Custom" and sets a custom range.
# Actually, since the user says "menentukan hingga hari dan jam nya", let's replace the quick range buttons with a simple <input type="datetime-local"> pair for start/end, OR just add it next to the quick filters!

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(code)

