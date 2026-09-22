import { useState, useEffect } from 'react';
import { Map as MapIcon, Layout, Maximize2, Minimize2 } from 'lucide-react';
import SegmentDetailModal, { SegmentData } from '../components/SegmentDetailModal';
import AlarmPopup from '../components/AlarmPopup';

// Components
import MapVisualization from '../features/map/MapVisualization';
import DiagramVisualization from '../features/map/DiagramVisualization';
import TopNavbar from '../components/layout/TopNavbar';
import LogPanel from '../features/dashboard/LogPanel';
import LeftPanel from '../features/dashboard/LeftPanel';
import SegmentStats from '../features/dashboard/SegmentStats';
import RightPanel from '../features/dashboard/RightPanel';
import DataModal from '../features/dashboard/DataModal';

import { getCurrentWindow } from '@tauri-apps/api/window';
import { invoke } from '@tauri-apps/api/core';

interface LiveSegment {
  id: number;
  dts_ch: number;
  dts_code: number;
  original_name: string;
  custom_name: string | null;
  main_group: string;
  sub_group: string | null;
  start_m?: number | null;
  end_m?: number | null;
  temp_avg: number;
  temp_min: number;
  temp_max: number;
  temp_min_p: number;
  temp_max_p: number;
}

export interface AlarmLog {
  id: number;
  time: string;
  ch: number;
  code: number;
  distance: number;
  alarm_type: number;
  temp: number;
  is_active: boolean;
}

export default function Dashboard() {
  const [viewMode, setViewMode] = useState<'satellite' | 'diagram'>('satellite');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [mapZoom, setMapZoom] = useState(15);
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true;
  });

  const [userRole, setUserRole] = useState('OPERATOR');
  const [userId, setUserId] = useState('OP-7729');

  const [mappings, setMappings] = useState<LiveSegment[]>([]);
  const [alarms, setAlarms] = useState<AlarmLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [activeMainGroup, setActiveMainGroup] = useState<string>('All');
  const [activeSubGroup, setActiveSubGroup] = useState<string>('All');

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSegment, setSelectedSegment] = useState<SegmentData | null>(null);
  
  const [showDataModal, setShowDataModal] = useState(false);
  const [categoryModal, setCategoryModal] = useState<'Total' | 'Normal' | 'Warning' | 'Danger' | null>(null);

  // Pagination for Left Panel
  const itemsPerPage = isFullscreen ? 2 : 4;
  const [currentPage, setCurrentPage] = useState(1);
  const [warningThreshold, setWarningThreshold] = useState(45);
  const [criticalThreshold, setCriticalThreshold] = useState(60);
  const [ackedAlarms, setAckedAlarms] = useState<Set<number>>(new Set());
  const [isPopupMuted, setIsPopupMuted] = useState(false);

    useEffect(() => {
    import('@tauri-apps/api/core').then(({ invoke }) => {
      invoke<Record<string, string>>('get_all_settings').then(settings => {
        if (settings['warning_threshold']) setWarningThreshold(Number(settings['warning_threshold']));
        if (settings['critical_threshold']) setCriticalThreshold(Number(settings['critical_threshold']));
      }).catch(console.error);
    });
  }, []);

  useEffect(() => {
    if ('__TAURI_INTERNALS__' in window) {
      const fetchLive = () => {
        import('@tauri-apps/api/core').then(({ invoke }) => {
          Promise.all([
            invoke<LiveSegment[]>('get_live_segments'),
            invoke<AlarmLog[]>('get_alarms')
          ]).then(([m, a]) => {
            setMappings(m);
            setAlarms(a);
            setHasError(false);
            setIsLoading(false);
          }).catch(err => {
            console.error("Failed to load live data", err);
            setHasError(true);
            setErrorMessage(typeof err === 'string' ? err : JSON.stringify(err));
            setIsLoading(false);
          });
        });
      };
      
      fetchLive(); // initial fetch
      const interval = setInterval(fetchLive, 5000); // Poll every 5 seconds
      return () => clearInterval(interval);
    }
  }, []);

  useEffect(() => {
    const role = localStorage.getItem('userRole');
    const id = localStorage.getItem('userId');
    if (role) setUserRole(role);
    if (id) setUserId(id);
  }, []);

  useEffect(() => {
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    document.documentElement.className = isDarkMode ? 'dark' : 'light';
  }, [isDarkMode]);

  // Sync state dengan Tauri Window Fullscreen
  useEffect(() => {
    try {
      const appWindow = getCurrentWindow();
      appWindow.setFullscreen(isFullscreen).catch(() => {});
    } catch (e) {
      // Abaikan jika jalan di browser biasa (bukan Tauri)
    }
  }, [isFullscreen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'F11' || e.key === 'f') {
        e.preventDefault();
        setIsFullscreen(prev => !prev);
      }
      if (e.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isFullscreen]);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // ------------------------------------------------
  // Filter, Grouping, and Pagination Logic
  // ------------------------------------------------
  const mainGroups = Array.from(new Set(mappings.map(m => m.main_group))).filter(g => g !== 'Unassigned');
  const subGroups = activeMainGroup !== 'All' 
    ? Array.from(new Set(mappings.filter(m => m.main_group === activeMainGroup && m.sub_group).map(m => m.sub_group as string)))
    : [];

  
  // Smart Naming Algorithm
  const groupedSegments: Record<string, LiveSegment[]> = {};
  mappings.forEach(m => {
    if (m.main_group && m.main_group !== 'Unassigned') {
      const prefix = m.sub_group ? m.sub_group : m.main_group;
      if (!groupedSegments[prefix]) groupedSegments[prefix] = [];
      groupedSegments[prefix].push(m);
    }
  });

  Object.keys(groupedSegments).forEach(prefix => {
    groupedSegments[prefix].sort((a, b) => (a.start_m || 0) - (b.start_m || 0));
    groupedSegments[prefix].forEach((m, index) => {
      (m as any).smart_name = `${prefix} - ${index + 1}`;
    });
  });

  const baseAreas: (SegmentData & { mainGroup: string; subGroup?: string })[] = mappings.map(m => {
      const isCableBroken = m.temp_max < -50;
      const isTempCritical = m.temp_max >= criticalThreshold;
      const isTempWarning = m.temp_max >= warningThreshold;
      
      const dbAlarm = alarms.find(a => a.is_active && a.ch === m.dts_ch && a.code === m.dts_code);
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
      }
      
      return {
        id: m.id,
        name: (m as any).smart_name || m.custom_name || m.original_name,
        distance: m.start_m != null && m.end_m != null ? `${m.start_m}m - ${m.end_m}m` : `CH${m.dts_ch}-C${m.dts_code}`,
        temp: m.temp_max, // Changed to display max temperature
        temp_avg: m.temp_avg,
        temp_min: m.temp_min,
        temp_max: m.temp_max,
        temp_min_p: m.temp_min_p,
        temp_max_p: m.temp_max_p,
        isAlarm, 
        status,
        mainGroup: m.main_group,
        subGroup: m.sub_group || undefined,
        mappingId: m.id,
        original_name: m.original_name,
        dts_ch: m.dts_ch,
        dts_code: m.dts_code,
        start_m: m.start_m ?? undefined,
        end_m: m.end_m ?? undefined,
      };
  });

  const filteredAreas = baseAreas.filter(area => {
    const matchesSearch = area.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesMain = activeMainGroup === 'All' || area.mainGroup === activeMainGroup;
    const matchesSub = activeSubGroup === 'All' || area.subGroup === activeSubGroup;
    return matchesSearch && matchesMain && matchesSub;
  });

  const totalPages = Math.ceil(filteredAreas.length / itemsPerPage);
  
  useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(1);
    }
  }, [totalPages, currentPage]);

  useEffect(() => {
    if (searchTerm) return;
    const timer = setInterval(() => {
      setCurrentPage(prev => (prev >= totalPages ? 1 : prev + 1));
    }, 5000);
    return () => clearInterval(timer);
  }, [totalPages, searchTerm]);

  const currentAreas = filteredAreas.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  // Stats
  const totalSegments = baseAreas.length;
  const normalSegments = baseAreas.filter(a => a.status === 'Normal').length;
  const warningSegments = baseAreas.filter(a => a.status.includes('WARN')).length;
  const dangerSegments = baseAreas.filter(a => a.isAlarm && !a.status.includes('WARN')).length;
  
  const dangerAreasList = filteredAreas.filter(a => a.isAlarm && !a.status.includes('WARN'));
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
  }, [unackedAlarms.map(a => a.id).join(',')]);

  return (
    <div className="h-screen bg-bg-base flex flex-col text-text-primary overflow-hidden font-sans">
      
      {/* RED PULSE OVERLAY FOR UNACKED ALARMS */}
      {unackedAlarms.length > 0 && !isPopupMuted && (
        <div className="absolute inset-0 pointer-events-none bg-red-600/15 animate-[pulse_2s_ease-in-out_infinite] z-40 mix-blend-overlay"></div>
      )}

      {/* TOP MENU BAR */}
      <TopNavbar 
        isFullscreen={isFullscreen}
        isDarkMode={isDarkMode}
        setIsDarkMode={setIsDarkMode}
        userRole={userRole}
        userId={userId}
      />


      {/* MAIN CONTENT AREA */}
      <div className="flex-1 relative overflow-hidden bg-bg-base flex">
        
        {hasError && (
          <div className="absolute top-0 left-0 right-0 z-50 bg-red-500/90 text-white text-xs font-bold font-mono tracking-widest text-center py-1">
            CONNECTION ERROR TO DTS MYSQL. RETRYING... ({errorMessage})
          </div>
        )}
        {isLoading && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-bg-base/80 backdrop-blur-sm">
            <div className="flex flex-col items-center">
              <div className="w-12 h-12 border-4 border-scada-primary border-t-transparent rounded-full animate-spin mb-4"></div>
              <p className="font-mono text-scada-primary font-bold tracking-widest text-lg animate-pulse">LOADING FIELD DATA...</p>
            </div>
          </div>
        )}
        
        {!isLoading && !hasError && mappings.length === 0 && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-bg-base/90 backdrop-blur-md">
            <div className="flex flex-col items-center max-w-lg text-center p-8 border border-border rounded-xl bg-bg-panel shadow-2xl">
              <Layout size={48} className="text-text-secondary mb-4" />
              <h3 className="font-bold text-2xl text-text-primary tracking-widest mb-2">NO SEGMENTS CONFIGURED</h3>
              <p className="text-text-secondary mb-6">Your dashboard is empty because no fiber segments have been mapped yet.</p>
              <button 
                onClick={() => window.location.href = '/settings'}
                className="px-6 py-3 bg-scada-primary text-black font-bold tracking-widest uppercase rounded hover:bg-scada-primary/90 transition-colors"
              >
                Go To Settings & Sync Data
              </button>
            </div>
          </div>
        )}

        
        {/* MAP/DIAGRAM VISUALIZATION (Background Layer) */}
        <div className="flex-1 relative flex bg-bg-panel/30 overflow-hidden">
          {viewMode === 'satellite' ? (
            <MapVisualization 
              isFullscreen={isFullscreen} 
              mapZoom={mapZoom} 
              setMapZoom={setMapZoom} 
              segments={mappings}
              warningThreshold={Number(warningThreshold)}
              criticalThreshold={Number(criticalThreshold)}
            />
          ) : (
            <DiagramVisualization isFullscreen={isFullscreen} segments={mappings} warningThreshold={warningThreshold} criticalThreshold={criticalThreshold} />
          )}

          {/* View Toolbar overlay (Right) */}
          <div className="absolute top-4 right-4 z-20 flex flex-col space-y-2">
            <div className="flex flex-col bg-bg-panel/80 backdrop-blur border border-border rounded-lg shadow-xl overflow-hidden pointer-events-auto">
              <button 
                onClick={(e) => { e.stopPropagation(); setViewMode('satellite'); }}
                className={`p-3 flex items-center justify-center transition-colors ${viewMode === 'satellite' ? 'bg-scada-primary text-text-primary' : 'text-text-secondary hover:text-text-primary hover:bg-bg-surface'}`}
                title="Satellite Map"
              >
                <MapIcon size={20} />
              </button>
              <div className="h-px w-full bg-border"></div>
              <button 
                onClick={(e) => { e.stopPropagation(); setViewMode('diagram'); }}
                className={`p-3 flex items-center justify-center transition-colors ${viewMode === 'diagram' ? 'bg-scada-primary text-text-primary' : 'text-text-secondary hover:text-text-primary hover:bg-bg-surface'}`}
                title="P&ID Diagram"
              >
                <Layout size={20} />
              </button>
            </div>

            <button 
              onClick={(e) => { e.stopPropagation(); setIsFullscreen(!isFullscreen); }}
              className="p-3 bg-bg-panel/80 hover:bg-bg-panel border border-border text-text-primary rounded-lg transition-colors backdrop-blur shadow-xl flex items-center justify-center mt-2 pointer-events-auto"
              title="Toggle Fullscreen"
            >
              {isFullscreen ? <Minimize2 size={20} /> : <Maximize2 size={20} />}
            </button>
          </div>
        </div>

        {/* GLOBAL LEGEND (Bottom Left) */}
        <div className={`absolute bottom-4 left-4 z-30 ${isFullscreen ? 'w-72' : 'w-96'} bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl shadow-lg p-3 pointer-events-auto transition-all duration-500 flex flex-col space-y-2`}>
          <div className="text-[10px] font-bold text-text-secondary uppercase tracking-widest border-b border-border pb-1">
            FIBER LINE STATUS
          </div>
          <div className="flex items-center justify-between px-1">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-1 bg-[#22c55e] rounded-full"></div>
              <span className="text-[11px] text-text-secondary font-mono">NORMAL</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-1 bg-yellow-500 rounded-full"></div>
              <span className="text-[11px] text-text-secondary font-mono">WARNING</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-1 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-[11px] text-red-400 font-mono font-bold">DANGER</span>
            </div>
          </div>
        </div>

        {/* FLOATING LEFT PANEL - AREA LIST */}
        <aside className={`absolute top-4 left-4 ${isFullscreen ? 'w-72 bottom-auto' : 'w-96 bottom-[90px]'} flex flex-col z-20 pointer-events-none space-y-4 transition-all duration-500`}>
          <SegmentStats 
            totalSegments={totalSegments}
            normalSegments={normalSegments}
            warningSegments={warningSegments}
            dangerSegments={dangerSegments}
            onCategoryClick={setCategoryModal}
          />
          <LeftPanel 
            isFullscreen={isFullscreen}
            searchTerm={searchTerm}
            setSearchTerm={setSearchTerm}
            setCurrentPage={setCurrentPage}
            currentAreas={currentAreas}
            setSelectedSegment={setSelectedSegment}
            totalPages={totalPages}
            currentPage={currentPage}
            setShowDataModal={setShowDataModal}
            mainGroups={mainGroups}
            activeMainGroup={activeMainGroup}
            setActiveMainGroup={setActiveMainGroup}
            subGroups={subGroups}
            activeSubGroup={activeSubGroup}
            setActiveSubGroup={setActiveSubGroup}
          />
          {!isFullscreen && (
            <RightPanel />
          )}
        </aside>

        {/* LOG & STATUS PANEL (BOTTOM RIGHT) */}
        <LogPanel 
          isFullscreen={isFullscreen}
          dummyLogs={alarms.map(a => ({
            id: a.id,
            time: new Date(a.time).toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
            msg: `Ch${a.ch}-C${a.code} at ${a.distance}m: ${a.alarm_type === 1 ? 'High Temp' : a.alarm_type === 2 ? 'Low Temp' : a.alarm_type === 3 ? 'Temp Rise' : a.alarm_type === 4 ? 'Fiber Break' : 'Anti-tamper'} (${a.temp}°C)`,
            type: a.is_active ? 'error' : 'info'
          }))}
          currentTime={currentTime}
        />

        {/* FULLSCREEN DATA MODAL */}
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
              if (categoryModal === 'Warning') return a.status.includes('WARN');
              if (categoryModal === 'Danger') return a.isAlarm && !a.status.includes('WARN');
              return false;
            })}
            setSelectedSegment={(seg) => {
               setCategoryModal(null);
               setSelectedSegment(seg);
            }}
          />
        )}

        {/* ALARM POPUP */}
        {!isPopupMuted && unackedAlarms.length > 0 && (
          <AlarmPopup 
            unackedAlarms={unackedAlarms}
            onAck={(ids) => {
              const newAcked = new Set(ackedAlarms);
              ids.forEach(id => newAcked.add(id));
              setAckedAlarms(newAcked);
              
              // Call backend to update MySQL AlarmResetTime
              import('@tauri-apps/api/core').then(({ invoke }) => {
                invoke('ack_all_alarms').catch(console.error);
              });
            }}
            onCancel={() => setIsPopupMuted(true)}
          />
        )}
        
        {/* SEGMENT DETAIL MODAL */}
        {selectedSegment && (
          <SegmentDetailModal 
            segment={selectedSegment} 
            onClose={() => setSelectedSegment(null)} 
            isAdmin={userRole === 'ADMINISTRATOR'}
            onRename={async (id, newName) => {
              try {
                const targetMapping = mappings.find(m => m.id === id);
                if (targetMapping) {
                  await invoke('update_segment_mapping', { 
                    id, 
                    customName: newName, 
                    mainGroup: targetMapping.main_group, 
                    subGroup: targetMapping.sub_group 
                  });
                  // Refetch mappings
                  const updated: LiveSegment[] = await invoke('get_segment_mappings');
                  setMappings(updated);
                  // Update selected segment so it doesn't revert if modal stays open
                  setSelectedSegment(prev => prev ? { ...prev, name: newName } : null);
                }
              } catch (err) {
                console.error("Failed to rename:", err);
              }
            }}
          />
        )}

      </div>
    </div>
  );
}
