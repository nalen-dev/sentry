import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    db = f.read()

# Fix categoryModal type
db = db.replace(
    "const [categoryModal, setCategoryModal] = useState<'Total' | 'Normal' | 'Warning' | 'Danger' | null>(null);",
    "const [categoryModal, setCategoryModal] = useState<'Total' | 'Normal' | 'HighTemp' | 'FiberBreak' | null>(null);"
)

# Fix the stats calculation
old_stats = """  const totalSegments = baseAreas.length;
  const alarmSegments = baseAreas.filter(a => a.isAlarm).length;
  const normalSegments = totalSegments - alarmSegments;
  const warningSegments = Math.floor(alarmSegments * 0.3);
  const dangerSegments = alarmSegments - warningSegments;"""

new_stats = """  const totalSegments = baseAreas.length;
  const normalSegments = baseAreas.filter(a => a.status === 'Normal').length;
  const highTempSegments = baseAreas.filter(a => a.status === 'Warning' || a.status === 'Critical').length;
  const fiberBreakSegments = baseAreas.filter(a => a.status === 'Broken Cable').length;"""

db = db.replace(old_stats, new_stats)

# Update SegmentStats props
old_ss_props = """          <SegmentStats 
            totalSegments={totalSegments}
            normalSegments={normalSegments}
            warningSegments={warningSegments}
            dangerSegments={dangerSegments}
            onCategoryClick={setCategoryModal}
          />"""

new_ss_props = """          <SegmentStats 
            totalSegments={totalSegments}
            normalSegments={normalSegments}
            highTempSegments={highTempSegments}
            fiberBreakSegments={fiberBreakSegments}
            onCategoryClick={setCategoryModal}
          />"""
db = db.replace(old_ss_props, new_ss_props)

# Update DataModal filter logic
old_modal_filter = """        {categoryModal && (
          <DataModal 
            onClose={() => setCategoryModal(null)}
            areas={baseAreas.filter(a => {
              if (categoryModal === 'Total') return true;
              if (categoryModal === 'Normal') return a.status === 'Normal';
              if (categoryModal === 'Warning') return a.status === 'Warning';
              return a.isAlarm; // Danger
            })}"""

new_modal_filter = """        {categoryModal && (
          <DataModal 
            onClose={() => setCategoryModal(null)}
            areas={baseAreas.filter(a => {
              if (categoryModal === 'Total') return true;
              if (categoryModal === 'Normal') return a.status === 'Normal';
              if (categoryModal === 'HighTemp') return a.status === 'Warning' || a.status === 'Critical';
              if (categoryModal === 'FiberBreak') return a.status === 'Broken Cable';
              return false;
            })}"""

db = db.replace(old_modal_filter, new_modal_filter)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(db)

