import re

with open('src/features/dashboard/LogPanel.tsx', 'r') as f:
    content = f.read()

old_block = """      {/* LOGOS */}
      <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl shadow-lg p-4 pointer-events-auto transition-all duration-300 flex items-center justify-center space-x-6">
        <img src="/logo-itm.png" alt="ITM Logo" className="h-10 object-contain" />
        <div className="h-8 w-px bg-border"></div>
        <img src="/logo-kag.jpeg" alt="KAG Logo" className="h-10 object-contain rounded-sm" />
      </div>"""

new_block = """      {/* LOGOS */}
      <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl shadow-lg p-3 pointer-events-auto transition-all duration-300 flex items-center justify-center space-x-4">
        <div className="bg-white rounded-md px-3 py-1.5 flex items-center justify-center h-12 shadow-sm">
          <img src="/logo-itm.png" alt="ITM Logo" className="h-full w-auto object-contain" />
        </div>
        <div className="h-8 w-px bg-border"></div>
        <div className="bg-white rounded-md px-3 py-1.5 flex items-center justify-center h-12 shadow-sm">
          <img src="/logo-kag.jpeg" alt="KAG Logo" className="h-full w-auto object-contain" />
        </div>
      </div>"""

content = content.replace(old_block, new_block)

with open('src/features/dashboard/LogPanel.tsx', 'w') as f:
    f.write(content)

