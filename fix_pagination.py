import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    db = f.read()

db = db.replace(
    "const itemsPerPage = 7;",
    "const itemsPerPage = isFullscreen ? 2 : 4;"
)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(db)

