import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

old_str = """          <SegmentDetailModal 
            segment={selectedSegment} 
            onClose={() => setSelectedSegment(null)} 
            isAdmin={userRole === 'ADMINISTRATOR'}"""

new_str = """          <SegmentDetailModal 
            segment={selectedSegment} 
            onClose={() => setSelectedSegment(null)} 
            warningThreshold={warningThreshold}
            criticalThreshold={criticalThreshold}
            isAdmin={userRole === 'ADMINISTRATOR'}"""

content = content.replace(old_str, new_str)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)

