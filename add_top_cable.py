import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# Add a 40m (32px) cable at the top (y=290) between BC4 B and BC5 (x=1209 to 1241)
top_cable_code = """          
          {/* 40m Cable at Top between BC4 B and BC5 */}
          <path d="M 1209,290 L 1241,290" fill="none" strokeWidth="3" className={getStrokeClass("BC4 B")} />"""

# We'll insert it right after the BC5 bottom fiber
old_bc5_fiber = """          <path d="M 1235,314 L 1355,314" fill="none" strokeWidth="3" className={getStrokeClass("BC5")} />"""
new_bc5_fiber = old_bc5_fiber + top_cable_code

code = code.replace(old_bc5_fiber, new_bc5_fiber)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

