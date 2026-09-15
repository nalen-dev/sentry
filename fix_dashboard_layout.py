import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    db = f.read()

# Imports
db = db.replace(
    "import LeftPanel from '../features/dashboard/LeftPanel';",
    "import LeftPanel from '../features/dashboard/LeftPanel';\nimport SegmentStats from '../features/dashboard/SegmentStats';"
)

# State for category modal
db = db.replace(
    "const [showDataModal, setShowDataModal] = useState(false);",
    "const [showDataModal, setShowDataModal] = useState(false);\n  const [categoryModal, setCategoryModal] = useState<'Total' | 'Normal' | 'Warning' | 'Danger' | null>(null);"
)

# Aside logic
old_aside = """        {/* FLOATING LEFT PANEL - AREA LIST */}
        <aside className={`absolute top-4 left-4 ${isFullscreen ? 'w-72 bottom-auto' : 'w-96 bottom-[90px]'} flex flex-col z-20 pointer-events-none space-y-4 transition-all duration-500`}>
          <LeftPanel"""

new_aside = """        {/* FLOATING LEFT PANEL - AREA LIST */}
        <aside className={`absolute top-4 left-4 ${isFullscreen ? 'w-72 bottom-auto' : 'w-96 bottom-[90px]'} flex flex-col z-20 pointer-events-none space-y-4 transition-all duration-500`}>
          <SegmentStats 
            totalSegments={totalSegments}
            normalSegments={normalSegments}
            warningSegments={warningSegments}
            dangerSegments={dangerSegments}
            onCategoryClick={setCategoryModal}
          />
          <LeftPanel"""

db = db.replace(old_aside, new_aside)

# DataModal for category
category_modal_comp = """        {/* FULLSCREEN DATA MODAL */}
        {showDataModal && (
          <DataModal 
            onClose={() => setShowDataModal(false)}
            areas={baseAreas}
            setSelectedSegment={setSelectedSegment}
          />
        )}"""
        
new_category_modal_comp = """        {/* FULLSCREEN DATA MODAL */}
        {showDataModal && (
          <DataModal 
            onClose={() => setShowDataModal(false)}
            areas={baseAreas}
            setSelectedSegment={setSelectedSegment}
          />
        )}
        
        {/* CATEGORY DATA MODAL */}
        {categoryModal && (
          <DataModal 
            onClose={() => setCategoryModal(null)}
            areas={baseAreas.filter(a => {
              if (categoryModal === 'Total') return true;
              if (categoryModal === 'Normal') return a.status === 'Normal';
              if (categoryModal === 'Warning') return a.status === 'Warning';
              return a.isAlarm; // Danger
            })}
            setSelectedSegment={(seg) => {
               setCategoryModal(null);
               setSelectedSegment(seg);
            }}
          />
        )}"""

db = db.replace(category_modal_comp, new_category_modal_comp)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(db)

