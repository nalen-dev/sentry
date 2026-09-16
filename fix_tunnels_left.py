import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# Replace Bottom Nodes rendering (TN TCM 1 - 6)
old_bottom_nodes = """          {/* Bottom Nodes (TN TCM 1 - 6, right side) */}
          {[
            { id: 'TN TCM 1', x: 600 },
            { id: 'TN TCM 2', x: 700 },
            { id: 'TN TCM 3', x: 800 },
            { id: 'TN TCM 4', x: 900 },
            { id: 'TN TCM 5', x: 1000 },
            { id: 'TN TCM 6', x: 1100 }
          ].map((node, i) => ("""

new_bottom_nodes = """          {/* Bottom Nodes (TN TCM 1 - 6, left side) */}
          {[
            { id: 'TN TCM 1', x: 60 },
            { id: 'TN TCM 2', x: 130 },
            { id: 'TN TCM 3', x: 200 },
            { id: 'TN TCM 4', x: 270 },
            { id: 'TN TCM 5', x: 340 },
            { id: 'TN TCM 6', x: 410 }
          ].map((node, i) => ("""

code = code.replace(old_bottom_nodes, new_bottom_nodes)

# Replace Fiber D (Bottom Tunnels) path definitions
old_fiber_d = """          {/* FIBER D (Bottom Tunnels TN TCM 1-6) */}
          <path d="M 610,372 L 610,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 710,372 L 710,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 810,372 L 810,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 910,372 L 910,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 1010,372 L 1010,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 1110,372 L 1110,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 610,330 L 1110,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 610,330 L 525,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 525,330 L 525,360" fill="none" strokeWidth="3" strokeDasharray="5,5" className={getStrokeClass("A-4")} />"""

new_fiber_d = """          {/* FIBER D (Bottom Tunnels TN TCM 1-6, Left Side) */}
          <path d="M 70,372 L 70,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 140,372 L 140,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 210,372 L 210,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 280,372 L 280,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 350,372 L 350,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 420,372 L 420,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 70,330 L 420,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 420,330 L 493,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 493,330 L 493,360" fill="none" strokeWidth="3" strokeDasharray="5,5" className={getStrokeClass("A-4")} />"""

code = code.replace(old_fiber_d, new_fiber_d)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

