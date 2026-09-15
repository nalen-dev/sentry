import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    db = f.read()

# Fix status assignment
old_status = """      const isAlarm = isCableBroken || isTempCritical || isDbAlarm;
      let status = 'Normal';
      if (isCableBroken) status = 'Broken Cable';
      else if (isTempCritical) status = 'Critical';
      else if (isTempWarning) status = 'Warning';
      else if (isDbAlarm) status = 'Alarm';"""

new_status = """      const dbAlarm = alarms.find(a => a.is_active && a.ch === m.dts_ch && a.code === m.dts_code);
      const isAlarm = isCableBroken || isTempCritical || !!dbAlarm;
      
      let status = 'Normal';
      if (isCableBroken) status = 'FIBER BREAK';
      else if (isTempCritical) status = 'HIGH TEMP (CRITICAL)';
      else if (isTempWarning) status = 'HIGH TEMP (WARN)';
      else if (dbAlarm) {
         if (dbAlarm.alarm_type === 1) status = 'HIGH TEMP';
         else if (dbAlarm.alarm_type === 2) status = 'LOW TEMP';
         else if (dbAlarm.alarm_type === 3) status = 'TEMP RISE';
         else if (dbAlarm.alarm_type === 4) status = 'FIBER BREAK';
         else status = 'SENSOR ALARM';
      }"""

db = db.replace(old_status, new_status)

# Revert Stats to Warning / Danger
old_stats_calc = """  const totalSegments = baseAreas.length;
  const normalSegments = baseAreas.filter(a => a.status === 'Normal').length;
  const highTempSegments = baseAreas.filter(a => a.status === 'Warning' || a.status === 'Critical').length;
  const fiberBreakSegments = baseAreas.filter(a => a.status === 'Broken Cable').length;"""

new_stats_calc = """  const totalSegments = baseAreas.length;
  const normalSegments = baseAreas.filter(a => a.status === 'Normal').length;
  const warningSegments = baseAreas.filter(a => a.status.includes('WARN')).length;
  const dangerSegments = baseAreas.filter(a => a.isAlarm && !a.status.includes('WARN')).length;"""

db = db.replace(old_stats_calc, new_stats_calc)

old_ss_props = """          <SegmentStats 
            totalSegments={totalSegments}
            normalSegments={normalSegments}
            highTempSegments={highTempSegments}
            fiberBreakSegments={fiberBreakSegments}
            onCategoryClick={setCategoryModal}
          />"""

new_ss_props = """          <SegmentStats 
            totalSegments={totalSegments}
            normalSegments={normalSegments}
            warningSegments={warningSegments}
            dangerSegments={dangerSegments}
            onCategoryClick={setCategoryModal}
          />"""

db = db.replace(old_ss_props, new_ss_props)

old_modal_filter = """        {categoryModal && (
          <DataModal 
            onClose={() => setCategoryModal(null)}
            areas={baseAreas.filter(a => {
              if (categoryModal === 'Total') return true;
              if (categoryModal === 'Normal') return a.status === 'Normal';
              if (categoryModal === 'HighTemp') return a.status === 'Warning' || a.status === 'Critical';
              if (categoryModal === 'FiberBreak') return a.status === 'Broken Cable';
              return false;
            })}"""

new_modal_filter = """        {categoryModal && (
          <DataModal 
            onClose={() => setCategoryModal(null)}
            areas={baseAreas.filter(a => {
              if (categoryModal === 'Total') return true;
              if (categoryModal === 'Normal') return a.status === 'Normal';
              if (categoryModal === 'Warning') return a.status.includes('WARN');
              if (categoryModal === 'Danger') return a.isAlarm && !a.status.includes('WARN');
              return false;
            })}"""

db = db.replace(old_modal_filter, new_modal_filter)

# Fix CategoryModal state type
db = db.replace(
    "const [categoryModal, setCategoryModal] = useState<'Total' | 'Normal' | 'HighTemp' | 'FiberBreak' | null>(null);",
    "const [categoryModal, setCategoryModal] = useState<'Total' | 'Normal' | 'Warning' | 'Danger' | null>(null);"
)

# Fix dangerAreasList logic (only show popups for Danger, not Warn)
old_danger_list = """const dangerAreasList = filteredAreas.filter(a => a.isAlarm && (a.status === 'Critical' || a.status === 'Broken Cable' || a.status === 'Alarm'));"""
new_danger_list = """const dangerAreasList = filteredAreas.filter(a => a.isAlarm && !a.status.includes('WARN'));"""
db = db.replace(old_danger_list, new_danger_list)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(db)

