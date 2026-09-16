import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# Insert the nodes before the SVG fiber routes
nodes_code = """
          {/* Top Nodes (TN BEK 3 - 6) */}
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

          {/* Bottom Nodes (TN TCM 1 - 6) */}
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
"""

# Find where to insert (before SENSING FIBER ROUTES)
code = code.replace("{/* SENSING FIBER ROUTES */}", nodes_code + "\n          {/* SENSING FIBER ROUTES */}")


# Now insert the fiber cables for these tunnels
fibers_code = """          {/* FIBER B (TN BEK 3, TN BEK 4) */}
          <path d="M 130,220 L 130,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 230,220 L 230,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 130,282 L 493,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 493,282 L 493,360" fill="none" strokeWidth="3" strokeDasharray="5,5" className={getStrokeClass("A-3")} />
          
          {/* FIBER A (TN BEK 5, TN BEK 6) */}
          <path d="M 330,220 L 330,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 430,220 L 430,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 330,274 L 513,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 513,274 L 513,360" fill="none" strokeWidth="3" strokeDasharray="5,5" className={getStrokeClass("A-2")} />
          
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
"""

code = code.replace("{/* MAIN TRUNK ROUTE */}", fibers_code + "\n          {/* MAIN TRUNK ROUTE */}")

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

