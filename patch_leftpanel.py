import re

with open('src/features/dashboard/LeftPanel.tsx', 'r') as f:
    code = f.read()

old_name_block = """<span className={`font-bold text-base drop-shadow-md ${area.isAlarm ? 'text-red-400' : 'text-text-primary'}`}>
                    {area.name}
                  </span>"""

new_name_block = """<span className={`font-bold text-base drop-shadow-md ${area.isAlarm ? 'text-red-400' : 'text-text-primary'}`}>
                    {area.name}
                  </span>
                  <div className="flex items-center space-x-1 mt-0.5">
                    {area.mainGroup && area.mainGroup !== 'Unassigned' && (
                       <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 bg-bg-surface text-text-secondary rounded border border-border/50">{area.mainGroup}</span>
                    )}
                    {area.subGroup && (
                       <span className="text-[9px] font-mono font-bold px-1.5 py-0.5 bg-scada-primary/10 text-scada-primary rounded border border-scada-primary/20">{area.subGroup}</span>
                    )}
                  </div>"""

code = code.replace(old_name_block, new_name_block)

with open('src/features/dashboard/LeftPanel.tsx', 'w') as f:
    f.write(code)

