import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    content = f.read()

# Replace the pin SVG in polyPoints branch
pin_old = """<path d="M0 -15 C 8 -15 12 -7 12 0 C 12 8 0 15 0 15 C 0 15 -12 8 -12 0 C -12 -7 -8 -15 0 -15" className={fillColor} />
                  <circle cx="0" cy="-5" r="4" fill="white" />"""
pin_new = """<circle cx="0" cy="0" r="8" className={fillColor} />
                  <circle cx="0" cy="0" r="4" fill="white" />"""
content = content.replace(pin_old, pin_new)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(content)

