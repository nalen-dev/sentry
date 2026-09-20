import re

with open('src/features/dashboard/LogPanel.tsx', 'r') as f:
    content = f.read()

old_block = """      {/* SYSTEM STATUS & TIME */}
      <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl shadow-lg p-3 pointer-events-auto transition-all duration-300 flex items-center justify-between">
        <div className="flex flex-col items-start pl-2">
          <span className="text-[10px] text-text-secondary uppercase font-bold tracking-widest">DTS Connection</span>
          <div className="flex items-center text-scada-success font-bold text-xs mt-1">
            <Wifi size={14} className="mr-1 animate-pulse" />
            ONLINE (MySQL)
          </div>
        </div>
        
        <div className="h-8 w-px bg-border"></div>
        
        <div className="flex flex-col items-end min-w-[120px] pr-2">
          <span className="text-[10px] font-bold text-text-secondary font-mono tracking-widest uppercase">
            {currentTime.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })}
          </span>
          <div className="flex items-center text-scada-primary font-mono font-bold text-base mt-0.5">
            <Clock size={14} className="mr-1.5" />
            {currentTime.toLocaleTimeString('en-GB', { hour12: false })}
          </div>
        </div>
      </div>"""

new_block = """      {/* LOGOS */}
      <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl shadow-lg p-4 pointer-events-auto transition-all duration-300 flex items-center justify-center space-x-6">
        <img src="/logo-itm.png" alt="ITM Logo" className="h-10 object-contain" />
        <div className="h-8 w-px bg-border"></div>
        <img src="/logo-kag.jpeg" alt="KAG Logo" className="h-10 object-contain rounded-sm" />
      </div>"""

content = content.replace(old_block, new_block)

with open('src/features/dashboard/LogPanel.tsx', 'w') as f:
    f.write(content)

