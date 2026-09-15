import re

with open('src/features/dashboard/LeftPanel.tsx', 'r') as f:
    lp = f.read()

old_card = """                <span className={`font-bold text-base drop-shadow-md ${area.isAlarm ? 'text-red-400' : 'text-text-primary'}`}>
                  {area.name}
                </span>
                {area.isAlarm && <AlertTriangle size={14} className="text-scada-alert animate-pulse" />}
              </div>
              <div className="flex justify-between items-end mt-auto pt-2">
                <span className="text-sm font-semibold text-text-primary drop-shadow-md">
                  {area.distance}
                </span>"""

new_card = """                <div className="flex flex-col">
                  <span className={`font-bold text-base drop-shadow-md ${area.isAlarm ? 'text-red-400' : 'text-text-primary'}`}>
                    {area.name}
                  </span>
                  {area.isAlarm && (
                    <span className="text-[10px] font-bold font-mono tracking-wider mt-1 px-2 py-0.5 rounded bg-red-500/20 text-red-400 w-fit">
                      {area.status}
                    </span>
                  )}
                </div>
                {area.isAlarm && <AlertTriangle size={14} className="text-scada-alert animate-pulse shrink-0" />}
              </div>
              <div className="flex justify-between items-end mt-auto pt-2">
                <span className="text-sm font-semibold text-text-primary drop-shadow-md">
                  {area.distance}
                </span>"""

lp = lp.replace(old_card, new_card)

with open('src/features/dashboard/LeftPanel.tsx', 'w') as f:
    f.write(lp)

