import { useState, useEffect } from 'react';
import { Map as MapIcon, Layout, Maximize2, Minimize2 } from 'lucide-react';
import SegmentDetailModal, { SegmentData } from '../components/SegmentDetailModal';

// Components
import MapVisualization from '../features/map/MapVisualization';
import DiagramVisualization from '../features/map/DiagramVisualization';
import TopNavbar from '../components/layout/TopNavbar';
import LogPanel from '../features/dashboard/LogPanel';
import LeftPanel from '../features/dashboard/LeftPanel';
import RightPanel from '../features/dashboard/RightPanel';
import DataModal from '../features/dashboard/DataModal';
import { DUMMY_AREAS, DUMMY_LOGS, DUMMY_CHART_DATA } from '../data/constants';

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
  const [activeMainGroup, setActiveMainGroup] = useState<string>('All');
  const [activeSubGroup, setActiveSubGroup] = useState<string>('All');

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSegment, setSelectedSegment] = useState<SegmentData | null>(null);
  
  const [showDataModal, setShowDataModal] = useState(false);

  // Pagination for Left Panel
  const itemsPerPage = 7;
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    if ('__TAURI_INTERNALS__' in window) {
      const fetchLive = () => {
        import('@tauri-apps/api/core').then(({ invoke }) => {
          invoke<LiveSegment[]>('get_live_segments')
            .then(setMappings)
            .catch(err => console.error("Failed to load live segments", err));
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

  const baseAreas: (SegmentData & { mainGroup: string; subGroup: string | null })[] = mappings.length > 0 
    ? mappings.map(m => ({
        id: m.id,
        name: m.custom_name || m.original_name,
        distance: m.start_m != null && m.end_m != null ? `${m.start_m}m - ${m.end_m}m` : `CH${m.dts_ch}-C${m.dts_code}`,
        temp: m.temp_avg,
        temp_avg: m.temp_avg,
        temp_min: m.temp_min,
        temp_max: m.temp_max,
        temp_min_p: m.temp_min_p,
        temp_max_p: m.temp_max_p,
        isAlarm: false, status: 'Normal',
        mainGroup: m.main_group,
        subGroup: m.sub_group,
        mappingId: m.id,
        original_name: m.original_name
      }))
    : DUMMY_AREAS.map(a => ({ ...a, mainGroup: 'Unassigned', subGroup: null, mappingId: undefined, original_name: undefined }));

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
  const alarmSegments = baseAreas.filter(a => a.isAlarm).length;
  const normalSegments = totalSegments - alarmSegments;
  const warningSegments = Math.floor(alarmSegments * 0.3);
  const dangerSegments = alarmSegments - warningSegments;

  return (
    <div className="h-screen bg-bg-base flex flex-col text-text-primary overflow-hidden font-sans">
      
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
        
        {/* MAP/DIAGRAM VISUALIZATION (Background Layer) */}
        <div className="flex-1 relative flex bg-bg-panel/30 overflow-hidden">
          {viewMode === 'satellite' ? (
            <MapVisualization 
              isFullscreen={isFullscreen} 
              mapZoom={mapZoom} 
              setMapZoom={setMapZoom} 
            />
          ) : (
            <DiagramVisualization isFullscreen={isFullscreen} />
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
            <RightPanel 
              totalSegments={totalSegments}
              normalSegments={normalSegments}
              warningSegments={warningSegments}
              dangerSegments={dangerSegments}
              dummyChartData={DUMMY_CHART_DATA}
            />
          )}
        </aside>

        {/* BOTTOM RIGHT FLOATING CONTAINER */}
        <LogPanel 
          isFullscreen={isFullscreen} 
          dummyLogs={DUMMY_LOGS} 
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
