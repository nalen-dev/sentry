import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    db = f.read()

# Imports
db = db.replace(
    "import SegmentDetailModal, { SegmentData } from '../components/SegmentDetailModal';",
    "import SegmentDetailModal, { SegmentData } from '../components/SegmentDetailModal';\nimport AlarmPopup from '../components/AlarmPopup';"
)

# States
db = db.replace(
    "const [criticalThreshold, setCriticalThreshold] = useState(60);",
    "const [criticalThreshold, setCriticalThreshold] = useState(60);\n  const [ackedAlarms, setAckedAlarms] = useState<Set<number>>(new Set());\n  const [isPopupMuted, setIsPopupMuted] = useState(false);"
)

# Unacked logic right after `const dangerSegments = ...`
old_stats = """  const totalSegments = baseAreas.length;
  const alarmSegments = baseAreas.filter(a => a.isAlarm).length;
  const normalSegments = totalSegments - alarmSegments;
  const warningSegments = Math.floor(alarmSegments * 0.3);
  const dangerSegments = alarmSegments - warningSegments;"""
  
new_stats = """  const totalSegments = baseAreas.length;
  const alarmSegments = baseAreas.filter(a => a.isAlarm).length;
  const normalSegments = totalSegments - alarmSegments;
  const warningSegments = Math.floor(alarmSegments * 0.3);
  const dangerSegments = alarmSegments - warningSegments;
  
  const dangerAreasList = filteredAreas.filter(a => a.isAlarm && (a.status === 'Critical' || a.status === 'Broken Cable' || a.status === 'Alarm'));
  const unackedAlarms = dangerAreasList.filter(a => !ackedAlarms.has(a.id));
  
  // Cleanup acked alarms that are no longer in danger
  useEffect(() => {
    if (dangerAreasList.length === 0 && ackedAlarms.size > 0) {
       setAckedAlarms(new Set());
    } else if (ackedAlarms.size > 0) {
       const newAcked = new Set(ackedAlarms);
       let changed = false;
       for (const id of ackedAlarms) {
         if (!dangerAreasList.find(a => a.id === id)) {
           newAcked.delete(id);
           changed = true;
         }
       }
       if (changed) setAckedAlarms(newAcked);
    }
  }, [dangerAreasList, ackedAlarms]);
  
  useEffect(() => {
     if (unackedAlarms.length > 0) {
        setIsPopupMuted(false); // Unmute when new unacked alarm arrives
     }
  }, [unackedAlarms.map(a => a.id).join(',')]);"""

db = db.replace(old_stats, new_stats)

# Add AlarmPopup component
popup_comp = """        {/* SEGMENT DETAIL MODAL */}
        {selectedSegment && ("""
        
new_popup_comp = """        {/* ALARM POPUP */}
        {!isPopupMuted && unackedAlarms.length > 0 && (
          <AlarmPopup 
            unackedAlarms={unackedAlarms}
            onAck={(ids) => {
              const newAcked = new Set(ackedAlarms);
              ids.forEach(id => newAcked.add(id));
              setAckedAlarms(newAcked);
            }}
            onCancel={() => setIsPopupMuted(true)}
          />
        )}
        
        {/* SEGMENT DETAIL MODAL */}
        {selectedSegment && ("""

db = db.replace(popup_comp, new_popup_comp)

# Fix Task 1: LeftPanel should ONLY show danger areas if there are any
old_pagination = """  const totalPages = Math.ceil(filteredAreas.length / itemsPerPage);
  
  useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(1);
    }
  }, [totalPages, searchTerm]);

  const currentAreas = filteredAreas.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);"""
  
new_pagination = """  const dangerFilteredAreas = filteredAreas.filter(a => a.isAlarm);
  const displayAreas = dangerFilteredAreas.length > 0 ? dangerFilteredAreas : filteredAreas;

  const totalPages = Math.ceil(displayAreas.length / itemsPerPage);
  
  useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(1);
    }
  }, [totalPages, searchTerm]);

  const currentAreas = displayAreas.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);"""

db = db.replace(old_pagination, new_pagination)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(db)

