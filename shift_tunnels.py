import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# 1. Shift Top Nodes (TN BEK 3-6)
code = code.replace("{ id: 'TN BEK 3', x: 235 }", "{ id: 'TN BEK 3', x: 215 }")
code = code.replace("{ id: 'TN BEK 4', x: 305 }", "{ id: 'TN BEK 4', x: 285 }")
code = code.replace("{ id: 'TN BEK 5', x: 375 }", "{ id: 'TN BEK 5', x: 355 }")
code = code.replace("{ id: 'TN BEK 6', x: 445 }", "{ id: 'TN BEK 6', x: 425 }")

# 2. Shift Bottom Nodes (TN TCM 1-6)
code = code.replace("{ id: 'TN TCM 1', x: 60 }", "{ id: 'TN TCM 1', x: 40 }")
code = code.replace("{ id: 'TN TCM 2', x: 130 }", "{ id: 'TN TCM 2', x: 110 }")
code = code.replace("{ id: 'TN TCM 3', x: 200 }", "{ id: 'TN TCM 3', x: 180 }")
code = code.replace("{ id: 'TN TCM 4', x: 270 }", "{ id: 'TN TCM 4', x: 250 }")
code = code.replace("{ id: 'TN TCM 5', x: 340 }", "{ id: 'TN TCM 5', x: 320 }")
code = code.replace("{ id: 'TN TCM 6', x: 410 }", "{ id: 'TN TCM 6', x: 390 }")

# 3. Shift FIBER B (TN BEK 3, TN BEK 4)
old_fiber_b = """          {/* FIBER B (TN BEK 3, TN BEK 4) */}
          <path d="M 255,220 L 255,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 325,220 L 325,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 255,282 L 493,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />"""
new_fiber_b = """          {/* FIBER B (TN BEK 3, TN BEK 4) */}
          <path d="M 235,220 L 235,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 305,220 L 305,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 235,282 L 493,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />"""
code = code.replace(old_fiber_b, new_fiber_b)

# 4. Shift FIBER A (TN BEK 5, TN BEK 6)
old_fiber_a = """          {/* FIBER A (TN BEK 5, TN BEK 6) */}
          <path d="M 395,220 L 395,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 465,220 L 465,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 395,274 L 513,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />"""
new_fiber_a = """          {/* FIBER A (TN BEK 5, TN BEK 6) */}
          <path d="M 375,220 L 375,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 445,220 L 445,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 375,274 L 513,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />"""
code = code.replace(old_fiber_a, new_fiber_a)

# 5. Shift FIBER D (TN TCM 1-6)
old_fiber_d = """          {/* FIBER D (Bottom Tunnels TN TCM 1-6, Left Side) */}
          <path d="M 80,372 L 80,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 150,372 L 150,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 220,372 L 220,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 290,372 L 290,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 360,372 L 360,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 430,372 L 430,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 80,314 L 430,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 430,314 L 493,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />"""
new_fiber_d = """          {/* FIBER D (Bottom Tunnels TN TCM 1-6, Left Side) */}
          <path d="M 60,372 L 60,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 130,372 L 130,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 200,372 L 200,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 270,372 L 270,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 340,372 L 340,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 410,372 L 410,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 60,314 L 410,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 410,314 L 493,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />"""
code = code.replace(old_fiber_d, new_fiber_d)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

