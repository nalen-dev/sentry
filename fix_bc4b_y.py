import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

old_bc4b = """          {/* Fiber BC4 B (starts at control room x=513, goes right to x=1225 on TOP of conveyor y=290) */}
          <path d="M 513,290 L 1225,290" fill="none" strokeWidth="3" className={getStrokeClass("BC4 B")} />
          
          {/* Fiber BC5 (starts from end of BC4 B x=1225, goes to x=1355 on TOP of conveyor y=290) */}
          <path d="M 1225,290 L 1235,290" fill="none" strokeWidth="2" className="stroke-border" strokeDasharray="2,2" />
          <path d="M 1235,290 L 1355,290" fill="none" strokeWidth="3" className={getStrokeClass("BC5")} />"""

new_bc4b = """          {/* Fiber BC4 B (starts at control room x=513, goes right to x=1225 on BOTTOM of conveyor y=314) */}
          <path d="M 513,314 L 1225,314" fill="none" strokeWidth="3" className={getStrokeClass("BC4 B")} />
          
          {/* Fiber BC5 (starts from end of BC4 B x=1225, goes to x=1355 on BOTTOM of conveyor y=314) */}
          <path d="M 1225,314 L 1235,314" fill="none" strokeWidth="2" className="stroke-border" strokeDasharray="2,2" />
          <path d="M 1235,314 L 1355,314" fill="none" strokeWidth="3" className={getStrokeClass("BC5")} />"""

code = code.replace(old_bc4b, new_bc4b)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

