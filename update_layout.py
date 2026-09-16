import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# Replace the specific SVG area
old_svg_content = """          {/* BC4 A (Left Conveyor - 591m) */}
          <rect x="40" y="290" width="595" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
          <text x="337" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="3">BC4 A (591m)</text>

          {/* BC4 B and BC5 (Right Conveyor - 1027m) */}
          <rect x="675" y="290" width="705" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
          <text x="800" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="2">BC4 B</text>
          
          <line x1="930" y1="292" x2="930" y2="312" className="stroke-border" strokeWidth="2" />
          <text x="965" y="305" className="fill-text-secondary" fontSize="10" fontStyle="italic" textAnchor="middle">150m</text>
          <line x1="1000" y1="292" x2="1000" y2="312" className="stroke-border" strokeWidth="2" />
          
          <text x="1190" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="2">BC5</text>
          <text x="1027" y="330" className="fill-text-secondary" fontSize="10" textAnchor="middle">Total: 1027m</text>"""

new_svg_content = """          {/* BC4 A (Left Conveyor, proportional 591m = ~473px) */}
          <rect x="40" y="290" width="473" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
          <text x="276" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="3">BC4 A</text>

          {/* BC4 B (Right Conveyor, proportional 877m = ~702px) */}
          <rect x="523" y="290" width="702" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
          <text x="874" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="2">BC4 B</text>
          
          {/* BC5 (Right End Conveyor, proportional 150m = ~120px) */}
          <rect x="1235" y="290" width="120" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
          <text x="1295" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="2">BC5</text>"""

code = code.replace(old_svg_content, new_svg_content)

# Update control room position
code = code.replace('transform="translate(635, 360)"', 'transform="translate(473, 360)"')

# Let's remove the irrelevant paths so they don't look weird with the new proportional layout
# We will draw simple fiber paths for BC4 A, BC4 B, and BC5
old_paths_start = "{/* SENSING FIBER ROUTES */}"
old_paths_end = "{/* MAIN TRUNK ROUTE BC MAIN 02 */}"

import re
code = re.sub(r'\{/\* SENSING FIBER ROUTES \*/\}.*?\{/\* MAIN TRUNK ROUTE BC MAIN 02 \*/\}', 
              r"""{/* SENSING FIBER ROUTES */}
          {/* Fiber BC4 A (starts at control room x=513, goes left to x=40) */}
          <path d="M 513,314 L 513,360" fill="none" strokeWidth="3" className="stroke-scada-primary" strokeDasharray="5,5" />
          <path d="M 513,314 L 40,314" fill="none" strokeWidth="3" className={getStrokeClass("BC4 A")} />
          
          {/* Fiber BC4 B (starts at control room x=513, goes right to x=1225) */}
          <path d="M 513,314 L 1225,314" fill="none" strokeWidth="3" className={getStrokeClass("BC4 B")} />
          
          {/* Fiber BC5 (starts from end of BC4 B x=1225, goes to x=1355) */}
          <path d="M 1225,314 L 1235,314" fill="none" strokeWidth="2" className="stroke-border" strokeDasharray="2,2" />
          <path d="M 1235,314 L 1355,314" fill="none" strokeWidth="3" className={getStrokeClass("BC5")} />
          
          {/* MAIN TRUNK ROUTE */}\n""", code, flags=re.DOTALL)

# Delete MAIN TRUNK ROUTE lines as we replaced it
code = re.sub(r'<path d="M 682,314 L 1380,314".*?\n.*?<path d="M 682,314 L 682,400".*?\n', '', code)


with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

