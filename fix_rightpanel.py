import re

with open('src/features/dashboard/RightPanel.tsx', 'r') as f:
    rp = f.read()

# Remove the system statistics block
old_stats = """      {/* SYSTEM STATISTICS */}
      <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl p-4 shadow-lg pointer-events-auto shrink-0 flex flex-col mt-4">
        <div className="text-sm font-bold text-text-primary uppercase tracking-widest flex items-center border-b border-border pb-2 mb-3">
          <Activity size={16} className="mr-2 text-scada-primary" /> SEGMENT STATS
        </div>
        <div className="grid grid-cols-4 gap-2 text-center">
          <div className="flex flex-col bg-bg-surface p-2 rounded border border-border">
            <span className="text-lg font-mono font-bold text-text-primary">{totalSegments}</span>
            <span className="text-[9px] text-text-secondary uppercase font-bold tracking-widest mt-1">Total</span>
          </div>
          <div className="flex flex-col bg-bg-surface p-2 rounded border border-border">
            <span className="text-lg font-mono font-bold text-scada-success">{normalSegments}</span>
            <span className="text-[9px] text-text-secondary uppercase font-bold tracking-widest mt-1">Normal</span>
          </div>
          <div className="flex flex-col bg-bg-surface p-2 rounded border border-border">
            <span className="text-lg font-mono font-bold text-yellow-500">{warningSegments}</span>
            <span className="text-[9px] text-text-secondary uppercase font-bold tracking-widest mt-1">Warn</span>
          </div>
          <div className="flex flex-col bg-bg-alarm/50 p-2 rounded border border-red-500/30">
            <span className="text-lg font-mono font-bold text-red-500">{dangerSegments}</span>
            <span className="text-[9px] text-red-400 uppercase font-bold tracking-widest mt-1">Danger</span>
          </div>
        </div>
      </div>"""

rp = rp.replace(old_stats, "")
# And change `<div onClick={() => navigate('/chart')} className="... mt-4 ...">` to `mt-0` since it's the first thing? Actually mt-4 is fine if we want space, but wait, it will be in the aside. Let's change `mt-4` to `mt-0` for TEMPERATURE CHART if it's the only one. Wait, in `Dashboard.tsx` the `<RightPanel />` is inside `<aside className="... space-y-4">`. So it doesn't need `mt-4`!

rp = rp.replace('min-h-0 mt-4 transition-colors group"', 'min-h-0 transition-colors group"')

with open('src/features/dashboard/RightPanel.tsx', 'w') as f:
    f.write(rp)

