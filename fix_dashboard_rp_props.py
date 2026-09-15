import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    db = f.read()

old_rp = """          {!isFullscreen && (
            <RightPanel 
              totalSegments={totalSegments}
              normalSegments={normalSegments}
              warningSegments={warningSegments}
              dangerSegments={dangerSegments}
              filteredAreas={filteredAreas}
            />
          )}"""

new_rp = """          {!isFullscreen && (
            <RightPanel />
          )}"""

db = db.replace(old_rp, new_rp)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(db)

