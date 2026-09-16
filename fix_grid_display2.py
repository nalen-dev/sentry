import re

with open('src/components/MappingGrid.tsx', 'r') as f:
    grid = f.read()

# Remove the Start/End inputs
grid = re.sub(r'<div className="flex space-x-2">\s*<div className="space-y-1\.5 flex-1">\s*<label className="text-xs font-bold text-text-secondary uppercase tracking-wider block">Start \(M\)</label>[\s\S]*?</div>\s*</div>', '', grid)

with open('src/components/MappingGrid.tsx', 'w') as f:
    f.write(grid)

