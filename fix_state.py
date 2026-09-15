import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    db = f.read()

db = db.replace(
    "const [currentPage, setCurrentPage] = useState(1);",
    "const [currentPage, setCurrentPage] = useState(1);\n  const [warningThreshold, setWarningThreshold] = useState(45);\n  const [criticalThreshold, setCriticalThreshold] = useState(60);"
)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(db)

