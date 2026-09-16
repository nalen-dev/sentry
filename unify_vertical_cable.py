import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# 1. Update Main Fibers and add the Single Vertical Trunk
old_main = """          {/* SENSING FIBER ROUTES */}
          {/* Fiber BC4 A (starts at control room x=513, goes left to x=40 on TOP of conveyor y=290) */}
          <path d="M 513,290 L 513,360" fill="none" strokeWidth="3" className="stroke-scada-primary" strokeDasharray="5,5" />
          <path d="M 513,290 L 40,290" fill="none" strokeWidth="3" className={getStrokeClass("BC4 A")} />"""

new_main = """          {/* SENSING FIBER ROUTES */}
          {/* Single Vertical Trunk bundle entering Control Room */}
          <path d="M 513,274 L 513,360" fill="none" strokeWidth="3" className="stroke-scada-primary" strokeDasharray="5,5" />
          
          {/* Fiber BC4 A (goes left to x=40 on TOP of conveyor y=290) */}
          <path d="M 513,290 L 40,290" fill="none" strokeWidth="3" className={getStrokeClass("BC4 A")} />"""
code = code.replace(old_main, new_main)

# 2. Update FIBER B to end horizontally at 513 and remove its vertical drop
old_fiber_b = """          {/* FIBER B (TN BEK 3, TN BEK 4) */}
          <path d="M 235,220 L 235,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 305,220 L 305,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 235,282 L 493,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 493,282 L 493,360" fill="none" strokeWidth="3" strokeDasharray="5,5" className={getStrokeClass("A-3")} />"""

new_fiber_b = """          {/* FIBER B (TN BEK 3, TN BEK 4) */}
          <path d="M 235,220 L 235,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 305,220 L 305,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 235,282 L 513,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />"""
code = code.replace(old_fiber_b, new_fiber_b)

# 3. Update FIBER D to end horizontally at 513 and remove its vertical drop
old_fiber_d = """          <path d="M 60,314 L 410,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 410,314 L 493,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 493,314 L 493,360" fill="none" strokeWidth="3" strokeDasharray="5,5" className={getStrokeClass("A-4")} />"""

new_fiber_d = """          <path d="M 60,314 L 410,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 410,314 L 513,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />"""

# We might also have to deal with the case if the code doesn't exactly match `410,314 L 493,314`
# Let's use regex to safely remove the `493,314 L 493,360` and replace `493` with `513` for the horizontal
code = re.sub(r'<path d="M 410,314 L 493,314" fill="none" strokeWidth="3" className=\{getStrokeClass\("A-4"\)\} />\n\s*<path d="M 493,314 L 493,360" fill="none" strokeWidth="3" strokeDasharray="5,5" className=\{getStrokeClass\("A-4"\)\} />',
              r'<path d="M 410,314 L 513,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />', code)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

