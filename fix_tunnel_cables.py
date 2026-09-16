import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# Replace FIBER B (TN BEK 3, TN BEK 4)
old_fiber_b = """          {/* FIBER B (TN BEK 3, TN BEK 4) */}
          <path d="M 245,220 L 245,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 315,220 L 315,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 245,282 L 493,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />"""

new_fiber_b = """          {/* FIBER B (TN BEK 3, TN BEK 4) */}
          <path d="M 255,220 L 255,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 325,220 L 325,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 255,282 L 493,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />"""

code = code.replace(old_fiber_b, new_fiber_b)

# Replace FIBER A (TN BEK 5, TN BEK 6)
old_fiber_a = """          {/* FIBER A (TN BEK 5, TN BEK 6) */}
          <path d="M 385,220 L 385,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 455,220 L 455,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 385,274 L 513,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />"""

new_fiber_a = """          {/* FIBER A (TN BEK 5, TN BEK 6) */}
          <path d="M 395,220 L 395,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 465,220 L 465,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 395,274 L 513,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />"""

code = code.replace(old_fiber_a, new_fiber_a)

# Replace FIBER D (Bottom Tunnels)
old_fiber_d = """          {/* FIBER D (Bottom Tunnels TN TCM 1-6, Left Side) */}
          <path d="M 70,372 L 70,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 140,372 L 140,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 210,372 L 210,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 280,372 L 280,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 350,372 L 350,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 420,372 L 420,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 70,330 L 420,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 420,330 L 493,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />"""

new_fiber_d = """          {/* FIBER D (Bottom Tunnels TN TCM 1-6, Left Side) */}
          <path d="M 80,372 L 80,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 150,372 L 150,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 220,372 L 220,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 290,372 L 290,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 360,372 L 360,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 430,372 L 430,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 80,330 L 430,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 430,330 L 493,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />"""

code = code.replace(old_fiber_d, new_fiber_d)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

