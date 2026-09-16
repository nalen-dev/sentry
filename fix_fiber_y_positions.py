import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# Fix Fiber BC4 A and Fiber BC4 B and BC5 (moving from y=314 to y=290)
old_main_fibers = """          {/* SENSING FIBER ROUTES */}
          {/* Fiber BC4 A (starts at control room x=513, goes left to x=40) */}
          <path d="M 513,314 L 513,360" fill="none" strokeWidth="3" className="stroke-scada-primary" strokeDasharray="5,5" />
          <path d="M 513,314 L 40,314" fill="none" strokeWidth="3" className={getStrokeClass("BC4 A")} />
          
          {/* Fiber BC4 B (starts at control room x=513, goes right to x=1225) */}
          <path d="M 513,314 L 1225,314" fill="none" strokeWidth="3" className={getStrokeClass("BC4 B")} />
          
          {/* Fiber BC5 (starts from end of BC4 B x=1225, goes to x=1355) */}
          <path d="M 1225,314 L 1235,314" fill="none" strokeWidth="2" className="stroke-border" strokeDasharray="2,2" />
          <path d="M 1235,314 L 1355,314" fill="none" strokeWidth="3" className={getStrokeClass("BC5")} />"""

new_main_fibers = """          {/* SENSING FIBER ROUTES */}
          {/* Fiber BC4 A (starts at control room x=513, goes left to x=40 on TOP of conveyor y=290) */}
          <path d="M 513,290 L 513,360" fill="none" strokeWidth="3" className="stroke-scada-primary" strokeDasharray="5,5" />
          <path d="M 513,290 L 40,290" fill="none" strokeWidth="3" className={getStrokeClass("BC4 A")} />
          
          {/* Fiber BC4 B (starts at control room x=513, goes right to x=1225 on TOP of conveyor y=290) */}
          <path d="M 513,290 L 1225,290" fill="none" strokeWidth="3" className={getStrokeClass("BC4 B")} />
          
          {/* Fiber BC5 (starts from end of BC4 B x=1225, goes to x=1355 on TOP of conveyor y=290) */}
          <path d="M 1225,290 L 1235,290" fill="none" strokeWidth="2" className="stroke-border" strokeDasharray="2,2" />
          <path d="M 1235,290 L 1355,290" fill="none" strokeWidth="3" className={getStrokeClass("BC5")} />"""

code = code.replace(old_main_fibers, new_main_fibers)

# Fix TCM horizontal line (moving from y=330 to y=314)
old_tcm_fibers = """          {/* FIBER D (Bottom Tunnels TN TCM 1-6, Left Side) */}
          <path d="M 80,372 L 80,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 150,372 L 150,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 220,372 L 220,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 290,372 L 290,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 360,372 L 360,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 430,372 L 430,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 80,330 L 430,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 430,330 L 493,330" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />"""

new_tcm_fibers = """          {/* FIBER D (Bottom Tunnels TN TCM 1-6, Left Side) */}
          <path d="M 80,372 L 80,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 150,372 L 150,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 220,372 L 220,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 290,372 L 290,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 360,372 L 360,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 430,372 L 430,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 80,314 L 430,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 430,314 L 493,314" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 493,314 L 493,360" fill="none" strokeWidth="3" strokeDasharray="5,5" className={getStrokeClass("A-4")} />"""

code = code.replace(old_tcm_fibers, new_tcm_fibers)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

