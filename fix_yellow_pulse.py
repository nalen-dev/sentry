import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# Make BOTH red and yellow lines pulse, and add drop shadow for yellow too
old_line_class = """${strokeColor} ${strokeColor.includes('red') ? 'animate-pulse drop-shadow-[0_0_8px_rgba(239,68,68,0.8)]' : ''}"""
new_line_class = """${strokeColor} ${isAlarm ? 'animate-pulse' : ''} ${strokeColor.includes('red') ? 'drop-shadow-[0_0_8px_rgba(239,68,68,0.8)]' : strokeColor.includes('yellow') ? 'drop-shadow-[0_0_8px_rgba(234,179,8,0.8)]' : ''}"""

code = code.replace(old_line_class, new_line_class)

# Make the pin itself pulse so the user sees the "titik berkedip"
old_pin_class = """className="animate-bounce\""""
new_pin_class = """className="animate-bounce animate-pulse\""""

code = code.replace(old_pin_class, new_pin_class)

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

