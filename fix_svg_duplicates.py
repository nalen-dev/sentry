import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# We will replace everything from `<svg ...>` to `</svg>`
new_svg = """        <svg viewBox="0 0 1450 600" className="w-[1600px] h-[660px] min-w-[1200px] drop-shadow-2xl -translate-y-8">
          
          <defs>
            <pattern id="dotGrid" width="30" height="30" patternUnits="userSpaceOnUse">
              <circle cx="2" cy="2" r="1" className="fill-border" />
            </pattern>
          </defs>
          
          <rect width="100%" height="100%" fill="url(#dotGrid)" />

          {/* BC4 A (Left Conveyor, proportional 591m = ~473px) */}
          <rect x="40" y="290" width="473" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
          <text x="276" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="3">BC4 A</text>

          {/* BC4 B (Right Conveyor, proportional 877m = ~702px) */}
          <rect x="523" y="290" width="702" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
          <text x="874" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="2">BC4 B</text>
          
          {/* BC5 (Right End Conveyor, proportional 150m = ~120px) */}
          <rect x="1235" y="290" width="120" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
          <text x="1295" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="2">BC5</text>

          {/* Top Nodes (TN BEK 3 - 6, before Control Room) */}
          {[
            { id: 'TN BEK 3', x: 120 },
            { id: 'TN BEK 4', x: 220 },
            { id: 'TN BEK 5', x: 320 },
            { id: 'TN BEK 6', x: 420 }
          ].map((node, i) => (
            <g key={`TF${i}`} transform={`translate(${node.x}, 220)`}>
              <rect width="20" height="50" className="fill-bg-surface stroke-border" strokeWidth="2" rx="3" />
              <text x="10" y="-12" className="fill-text-secondary" fontSize="11" fontWeight="bold" textAnchor="middle">{node.id}</text>
            </g>
          ))}

          {/* Bottom Nodes (TN TCM 1 - 6, right side) */}
          {[
            { id: 'TN TCM 1', x: 600 },
            { id: 'TN TCM 2', x: 700 },
            { id: 'TN TCM 3', x: 800 },
            { id: 'TN TCM 4', x: 900 },
            { id: 'TN TCM 5', x: 1000 },
            { id: 'TN TCM 6', x: 1100 }
          ].map((node, i) => (
            <g key={`BF${i}`} transform={`translate(${node.x}, 332)`}>
              <rect width="20" height="40" className="fill-bg-surface stroke-border" strokeWidth="2" rx="3" />
              <text x="10" y="64" className="fill-text-secondary" fontSize="11" fontWeight="bold" textAnchor="middle">{node.id}</text>
            </g>
          ))}

          {/* SENSING FIBER ROUTES */}
          {/* Fiber BC4 A (starts at control room x=513, goes left to x=40) */}
          <path d="M 513,314 L 513,360" fill="none" strokeWidth="3" className="stroke-scada-primary" strokeDasharray="5,5" />
          <path d="M 513,314 L 40,314" fill="none" strokeWidth="3" className={getStrokeClass("BC4 A")} />
          
          {/* Fiber BC4 B (starts at control room x=513, goes right to x=1225) */}
          <path d="M 513,314 L 1225,314" fill="none" strokeWidth="3" className={getStrokeClass("BC4 B")} />
          
          {/* Fiber BC5 (starts from end of BC4 B x=1225, goes to x=1355) */}
          <path d="M 1225,314 L 1235,314" fill="none" strokeWidth="2" className="stroke-border" strokeDasharray="2,2" />
          <path d="M 1235,314 L 1355,314" fill="none" strokeWidth="3" className={getStrokeClass("BC5")} />
          
          {/* FIBER B (TN BEK 3, TN BEK 4) */}
          <path d="M 130,220 L 130,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 230,220 L 230,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 130,282 L 493,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 493,282 L 493,360" fill="none" strokeWidth="3" strokeDasharray="5,5" className={getStrokeClass("A-3")} />
          
          {/* FIBER A (TN BEK 5, TN BEK 6) */}
          <path d="M 330,220 L 330,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 430,220 L 430,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 330,274 L 513,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          
          {/* FIBER D (Bottom Tunnels TN TCM 1-6) */}
          <path d="M 610,372 L 610,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 710,372 L 710,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 810,372 L 810,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 910,372 L 910,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 1010,372 L 1010,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 1110,372 L 1110,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 610,330 L 1110,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 610,330 L 525,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 525,330 L 525,360" fill="none" strokeWidth="3" strokeDasharray="5,5" className={getStrokeClass("A-4")} />

          {/* SYSTEM CONTROL ROOM */}
          <g transform="translate(473, 360)">
            <rect x="0" y="0" width="80" height="80" className="fill-bg-panel stroke-border" strokeWidth="2" rx="6" />
            <circle cx="40" cy="40" r="14" className="fill-bg-surface stroke-scada-primary" strokeWidth="3" />
            <text x="40" y="100" className="fill-text-primary" fontSize="11" fontWeight="bold" textAnchor="middle">CONTROL</text>
            <text x="40" y="114" className="fill-text-primary" fontSize="11" fontWeight="bold" textAnchor="middle">ROOM</text>
          </g>
        </svg>"""

code = re.sub(r'<svg viewBox="0 0 1450 600".*?</svg>', new_svg, code, flags=re.DOTALL)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

