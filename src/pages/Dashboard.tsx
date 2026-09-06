import { useState, useEffect } from 'react';
import { List, X, Grid, AlertTriangle, Map as MapIcon, Layout, Maximize2, Minimize2 } from 'lucide-react';
import SegmentDetailModal, { SegmentData } from '../components/SegmentDetailModal';

// Components
import TopNavbar from '../components/layout/TopNavbar';
import MapVisualization from '../features/map/MapVisualization';
import DiagramVisualization from '../features/map/DiagramVisualization';
import LeftPanel from '../features/dashboard/LeftPanel';
import RightPanel from '../features/dashboard/RightPanel';
import LogPanel from '../features/dashboard/LogPanel';

// Data
import { DUMMY_AREAS, DUMMY_LOGS, DUMMY_CHART_DATA } from '../data/constants';

export default function Dashboard() {
  const [viewMode, setViewMode] = useState<'satellite' | 'diagram'>('satellite');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [mapZoom, setMapZoom] = useState(15);
  const [isDarkMode, setIsDarkMode] = useState(true);

  const [userRole, setUserRole] = useState('OPERATOR');
  const [userId, setUserId] = useState('OP-7729');

  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  const [selectedSegment, setSelectedSegment] = useState<SegmentData | null>(null);
  
  const [showDataModal, setShowDataModal] = useState(false);
  const [modalViewMode, setModalViewMode] = useState<'grid' | 'table'>('grid');

  useEffect(() => {
    const role = localStorage.getItem('userRole');
    const id = localStorage.getItem('userId');
    if (role) setUserRole(role);
    if (id) setUserId(id);
  }, []);

  useEffect(() => {
    document.documentElement.className = isDarkMode ? 'dark' : 'light';
  }, [isDarkMode]);

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

  // Filter and Pagination Logic
  const filteredAreas = DUMMY_AREAS.filter(a => a.name.toLowerCase().includes(searchTerm.toLowerCase()));
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
  const totalSegments = DUMMY_AREAS.length;
  const dangerSegments = DUMMY_AREAS.filter(a => a.isAlarm).length;
  const warningSegments = DUMMY_AREAS.filter(a => parseFloat(a.temp) >= 45 && !a.isAlarm).length;
  const normalSegments = totalSegments - dangerSegments - warningSegments;

  return (
    <div className="h-screen bg-bg-base flex flex-col text-text-primary overflow-hidden font-sans">
      
      {/* TOP MENU BAR */}
      <TopNavbar 
        isFullscreen={isFullscreen}
        setIsFullscreen={setIsFullscreen}
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
          <div className="absolute inset-0 z-50 flex flex-col bg-bg-base/95 backdrop-blur-md p-8 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex justify-between items-center mb-6">
              <div className="flex items-center">
                <List className="text-scada-primary mr-3" size={28} />
                <div>
                  <h2 className="text-text-primary font-bold tracking-widest text-2xl uppercase">COMPLETE SEGMENT DATA</h2>
                  <p className="text-text-secondary font-mono text-sm">ALL DTS SEGMENTS MONITORING</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className="flex bg-bg-panel/50 p-1 rounded-lg border border-border">
                  <button
                    onClick={() => setModalViewMode('grid')}
                    className={`p-2 rounded-md flex items-center transition-all ${modalViewMode === 'grid' ? 'bg-bg-surface text-text-primary shadow-sm border border-border' : 'text-text-secondary hover:text-text-primary border border-transparent'}`}
                    title="Grid View"
                  >
                    <Grid size={18} />
                  </button>
                  <button
                    onClick={() => setModalViewMode('table')}
                    className={`p-2 rounded-md flex items-center transition-all ${modalViewMode === 'table' ? 'bg-bg-surface text-text-primary shadow-sm border border-border' : 'text-text-secondary hover:text-text-primary border border-transparent'}`}
                    title="Table View"
                  >
                    <List size={18} />
                  </button>
                </div>

                <button 
                  onClick={() => setShowDataModal(false)}
                  className="p-3 bg-red-500/10 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors border border-red-500/30"
                  title="Close"
                >
                  <X size={24} />
                </button>
              </div>
            </div>

            <div className="flex-1 bg-bg-panel border border-border rounded-xl overflow-hidden flex flex-col shadow-2xl relative">
              
              {/* TABLE VIEW */}
              {modalViewMode === 'table' && (
                <div className="overflow-x-auto flex-1 custom-scrollbar">
                  <table className="w-full text-left border-collapse">
                    <thead className="bg-bg-surface sticky top-0 z-10 shadow-md">
                      <tr>
                        <th className="py-4 px-6 text-text-secondary font-bold uppercase text-xs tracking-wider border-b border-border">Segment ID</th>
                        <th className="py-4 px-6 text-text-secondary font-bold uppercase text-xs tracking-wider border-b border-border">Area Name</th>
                        <th className="py-4 px-6 text-text-secondary font-bold uppercase text-xs tracking-wider border-b border-border">Distance (Meter)</th>
                        <th className="py-4 px-6 text-text-secondary font-bold uppercase text-xs tracking-wider border-b border-border">Current Temp</th>
                        <th className="py-4 px-6 text-text-secondary font-bold uppercase text-xs tracking-wider border-b border-border text-center">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {DUMMY_AREAS.map((area, idx) => (
                        <tr key={area.id} onClick={() => setSelectedSegment(area)} className={`cursor-pointer hover:bg-white/[0.02] transition-colors ${area.isAlarm ? 'bg-red-950/20' : ''}`}>
                          <td className="py-3 px-6 font-mono text-text-secondary text-sm">#{String(idx + 1).padStart(3, '0')}</td>
                          <td className="py-3 px-6 font-bold text-text-primary">{area.name}</td>
                          <td className="py-3 px-6 font-mono text-text-secondary">{area.distance}</td>
                          <td className={`py-3 px-6 font-mono font-bold ${area.isAlarm ? 'text-red-400' : 'text-scada-success'}`}>
                            {area.temp}°C
                          </td>
                          <td className="py-3 px-6 text-center">
                            {area.isAlarm ? (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-red-500/20 text-red-400 border border-red-500/30 shadow-[0_0_10px_rgba(240,71,71,0.3)]">
                                <AlertTriangle size={12} className="mr-1 animate-pulse" /> ALARM
                              </span>
                            ) : (
                              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-green-500/10 text-scada-success border border-green-500/20">
                                NORMAL
                              </span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* GRID VIEW */}
              {modalViewMode === 'grid' && (
                <div className="overflow-y-auto flex-1 custom-scrollbar p-6">
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-7 2xl:grid-cols-8 gap-4">
                    {DUMMY_AREAS.map(area => (
                      <div 
                        key={area.id} 
                        onClick={() => setSelectedSegment(area)}
                        className={`p-4 rounded-xl flex flex-col cursor-pointer transition-all hover:scale-105 shadow-xl backdrop-blur-sm border
                          ${area.isAlarm 
                            ? 'bg-bg-alarm border-red-500/50 shadow-[0_0_15px_rgba(240,71,71,0.3)]' 
                            : 'bg-bg-surface/80 border-border hover:bg-bg-surface'}`}
                      >
                        <div className="flex justify-between items-start mb-4">
                          <span className={`font-bold text-sm drop-shadow-md ${area.isAlarm ? 'text-red-400' : 'text-text-primary'}`}>
                            {area.name}
                          </span>
                          {area.isAlarm && <AlertTriangle size={14} className="text-red-500 animate-pulse" />}
                        </div>
                        <div className="flex justify-between items-end mt-auto">
                          <span className="text-xs font-semibold text-text-secondary drop-shadow-md">
                            {area.distance}
                          </span>
                          <span className={`text-base font-mono font-bold drop-shadow-md ${area.isAlarm ? 'text-red-400' : 'text-scada-success'}`}>
                            {area.temp}°C
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          </div>
        )}

        {/* SEGMENT DETAIL MODAL */}
        {selectedSegment && (
          <SegmentDetailModal 
            segment={selectedSegment} 
            onClose={() => setSelectedSegment(null)} 
            userRole={userRole}
          />
        )}

      </div>
    </div>
  );
}
