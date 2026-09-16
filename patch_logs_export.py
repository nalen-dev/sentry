import re

with open('src/pages/LogsPage.tsx', 'r') as f:
    code = f.read()

code = code.replace("import { invoke } from '@tauri-apps/api/core';", "import { invoke } from '@tauri-apps/api/core';\nimport { exportElementToPDF } from '../utils/exportPdf';")

code = code.replace('<div className="bg-bg-panel border border-border rounded-xl flex-1 flex flex-col shadow-lg overflow-hidden">', '<div id="logs-export-container" className="bg-bg-panel border border-border rounded-xl flex-1 flex flex-col shadow-lg overflow-hidden">')

old_export = """<button className="flex items-center px-4 py-2 bg-bg-panel border border-border rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-surface transition-colors font-bold text-sm shadow-sm">
              <Download size={16} className="mr-2" /> EXPORT PDF/CSV
            </button>"""

new_export = """<button onClick={() => exportElementToPDF('logs-export-container', `DTS_Logs_${new Date().getTime()}`)} className="flex items-center px-4 py-2 bg-bg-panel border border-border rounded-lg text-text-secondary hover:text-text-primary hover:bg-bg-surface transition-colors font-bold text-sm shadow-sm">
              <Download size={16} className="mr-2" /> EXPORT PDF
            </button>"""

code = code.replace(old_export, new_export)

with open('src/pages/LogsPage.tsx', 'w') as f:
    f.write(code)

