import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# Replace TN BEK 3-6 coordinates
old_bek_nodes = """          {/* Top Nodes (TN BEK 3 - 6, before Control Room) */}
          {[
            { id: 'TN BEK 3', x: 120 },
            { id: 'TN BEK 4', x: 220 },
            { id: 'TN BEK 5', x: 320 },
            { id: 'TN BEK 6', x: 420 }
          ].map((node, i) => ("""

new_bek_nodes = """          {/* Top Nodes (TN BEK 3 - 6, before Control Room) */}
          {[
            { id: 'TN BEK 3', x: 235 },
            { id: 'TN BEK 4', x: 305 },
            { id: 'TN BEK 5', x: 375 },
            { id: 'TN BEK 6', x: 445 }
          ].map((node, i) => ("""

code = code.replace(old_bek_nodes, new_bek_nodes)

# Replace Fiber B and Fiber A paths
old_fibers = """          {/* FIBER B (TN BEK 3, TN BEK 4) */}
          <path d="M 130,220 L 130,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 230,220 L 230,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 130,282 L 493,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 493,282 L 493,360" fill="none" strokeWidth="3" strokeDasharray="5,5" className={getStrokeClass("A-3")} />
          
          {/* FIBER A (TN BEK 5, TN BEK 6) */}
          <path d="M 330,220 L 330,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 430,220 L 430,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 330,274 L 513,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />"""

new_fibers = """          {/* FIBER B (TN BEK 3, TN BEK 4) */}
          <path d="M 245,220 L 245,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 315,220 L 315,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 245,282 L 493,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 493,282 L 493,360" fill="none" strokeWidth="3" strokeDasharray="5,5" className={getStrokeClass("A-3")} />
          
          {/* FIBER A (TN BEK 5, TN BEK 6) */}
          <path d="M 385,220 L 385,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 455,220 L 455,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 385,274 L 513,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />"""

code = code.replace(old_fibers, new_fibers)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

