import re

# Fix ChartPage
with open('src/pages/ChartPage.tsx', 'r') as f:
    chart_code = f.read()

# Add onClick to ChartPage export button if missing
if "exportElementToPDF" in chart_code and "exportElementToPDF(" not in chart_code:
    old_export = """<button className="flex items-center px-4 py-2 bg-bg-panel border border-border rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-surface transition-colors font-bold text-sm shadow-sm">
              <Download size={16} className="mr-2" /> EXPORT CSV
            </button>"""
    new_export = """<button onClick={() => exportElementToPDF('chart-export-container', `DTS_Chart_${chartMode}_${new Date().getTime()}`)} className="flex items-center px-4 py-2 bg-bg-panel border border-border rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-surface transition-colors font-bold text-sm shadow-sm">
              <Download size={16} className="mr-2" /> EXPORT PDF
            </button>"""
    chart_code = chart_code.replace(old_export, new_export)

# Another variant of the export button that might be there
if "exportElementToPDF(" not in chart_code:
    old_export2 = """<button onClick={handleExportCsv} className="flex items-center px-4 py-2 bg-bg-panel border border-border rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-surface transition-colors font-bold text-sm shadow-sm">
              <Download size={16} className="mr-2" /> EXPORT CSV
            </button>"""
    new_export2 = """<button onClick={() => exportElementToPDF('chart-export-container', `DTS_Chart_${chartMode}_${new Date().getTime()}`)} className="flex items-center px-4 py-2 bg-bg-panel border border-border rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-surface transition-colors font-bold text-sm shadow-sm">
              <Download size={16} className="mr-2" /> EXPORT PDF
            </button>"""
    chart_code = chart_code.replace(old_export2, new_export2)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(chart_code)


# Fix LogsPage
with open('src/pages/LogsPage.tsx', 'r') as f:
    logs_code = f.read()

# Remove DUMMY_AREAS
logs_code = logs_code.replace("import { DUMMY_AREAS } from '../data/constants';", "")

# Add invoke and exportElementToPDF
if "import { invoke }" not in logs_code:
    logs_code = logs_code.replace("import { useState, useEffect } from 'react';", "import { useState, useEffect } from 'react';\nimport { invoke } from '@tauri-apps/api/core';\nimport { exportElementToPDF } from '../utils/exportPdf';")

with open('src/pages/LogsPage.tsx', 'w') as f:
    f.write(logs_code)

