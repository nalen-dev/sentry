import { useState, useEffect } from 'react';
import { Activity, Settings, Sun, Moon, Maximize2, Minimize2, Map as MapIcon, Layout, AlertTriangle, Wifi, Clock, History, Search, List, X, Grid, LineChart, User, MapPin } from 'lucide-react';
import { MapContainer, TileLayer, Polyline, Tooltip, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';

// Komponen helper untuk mengontrol map secara dinamis
function MapController({ isFullscreen }: { isFullscreen: boolean }) {
  const map = useMap();

  useEffect(() => {
    // Kordinat ujung-ke-ujung conveyor
    const conveyorBounds: L.LatLngBoundsExpression = [
      [-0.3076283024687055, 115.85749409146369], // SW
      [-0.29970261465644, 115.86817796519595]  // NE
    ];

    if (isFullscreen) {
      map.dragging.enable();
      map.scrollWheelZoom.enable();
      map.doubleClickZoom.enable();
      map.touchZoom.enable();
      map.keyboard.enable();
    } else {
      map.dragging.disable();
      map.scrollWheelZoom.disable();
      map.doubleClickZoom.disable();
      map.touchZoom.disable();
      map.keyboard.disable();
      // Snap kembali ke kordinat overview yang pas saat mode default
      // Mengurangi padding sekecil mungkin (kecuali kiri untuk panel) 
      // agar peta bisa melakukan zoom-in sedekat/semaksimal mungkin.
      map.fitBounds(conveyorBounds, { 
        paddingTopLeft: [420, 10],      // [Kiri (kompensasi panel), Atas]
        paddingBottomRight: [10, 10]    // [Kanan, Bawah] dibuat sekecil mungkin
      });
    }
  }, [isFullscreen, map]);

  return null;
}

export default function Dashboard() {
  const [viewMode, setViewMode] = useState<'satellite' | 'diagram'>('satellite');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());
  
  // Area List States
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [showDataModal, setShowDataModal] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);
  const [modalViewMode, setModalViewMode] = useState<'table' | 'grid'>('grid');
  const itemsPerPage = 10;

  // Real-time clock
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Dummy area data based on request (increased to 42 for pagination testing)
  const areas = Array.from({ length: 42 }, (_, i) => ({
    id: `A-${i + 1}`,
    name: `Segment ${i + 1}`,
    distance: `${(i + 1) * 150}m`,
    temp: (30 + Math.random() * 20).toFixed(1),
    isAlarm: Math.random() > 0.95 // 5% chance of alarm
  }));

  // Filter and Pagination Logic
  const filteredAreas = areas.filter(a => a.name.toLowerCase().includes(searchTerm.toLowerCase()));
  const totalPages = Math.ceil(filteredAreas.length / itemsPerPage);
  
  // Reset page if search causes current page to exceed total pages
  useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(1);
    }
  }, [totalPages, currentPage]);

  // Auto-pagination
  useEffect(() => {
    if (searchTerm) return; // Don't auto-paginate while searching
    
    const timer = setInterval(() => {
      setCurrentPage(prev => (prev >= totalPages ? 1 : prev + 1));
    }, 5000);

    return () => clearInterval(timer);
  }, [totalPages, searchTerm]);

  const currentAreas = filteredAreas.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  // Stats
  // Stats
  const totalSegments = areas.length;
  const dangerSegments = areas.filter(a => a.isAlarm).length;
  const warningSegments = areas.filter(a => parseFloat(a.temp) >= 45 && !a.isAlarm).length;
  const normalSegments = totalSegments - dangerSegments - warningSegments;

  // Dummy Logs
  const dummyLogs = [
    { id: 1, time: '13:39:12', msg: 'System initialized successfully', type: 'info' },
    { id: 2, time: '13:40:05', msg: 'Calibration check on BC Main-01', type: 'info' },
    { id: 3, time: '13:41:22', msg: 'Warning threshold exceeded at TF3', type: 'warn' },
    { id: 4, time: '13:41:45', msg: 'Danger! Fire detected at VBF3', type: 'error' },
    { id: 5, time: '13:42:01', msg: 'User Administrator logged in', type: 'info' },
  ];

  // Dummy Chart Data
  const dummyChartData = [
    { time: '13:00', temp: 32 },
    { time: '13:10', temp: 35 },
    { time: '13:20', temp: 40 },
    { time: '13:30', temp: 55 },
    { time: '13:40', temp: 84 }, // Spike
    { time: '13:50', temp: 62 },
  ];

  return (
    <div className="h-screen bg-bg-base flex flex-col text-text-primary overflow-hidden font-sans">
      
      {/* TOP MENU BAR */}
      {!isFullscreen && (
        <header className="h-16 bg-bg-panel border-b border-border flex items-center px-6 shrink-0 justify-between shadow-md z-30">
          
          {/* TITLE */}
          <div className="flex items-center">
            <div>
              <h1 className="text-xl font-bold text-text-primary tracking-widest uppercase flex items-center">
                <Activity className="text-scada-primary mr-2" size={24} />
                DTS GIS INTEGRATION
              </h1>
              <p className="text-xs text-text-secondary font-mono">FIBER OPTIC MONITORING</p>
            </div>
          </div>
          
          {/* NAVIGATION & USER */}
          <div className="flex items-center space-x-6">
            
            <nav className="flex items-center space-x-6 mr-4">
              <button className="text-scada-primary font-bold text-sm transition-colors flex items-center tracking-widest">
                <Layout size={16} className="mr-2" /> DASHBOARD
              </button>
              <button className="text-text-secondary hover:text-text-primary font-bold text-sm transition-colors flex items-center tracking-widest">
                <History size={16} className="mr-2" /> LOGS
              </button>
              <button className="text-text-secondary hover:text-text-primary font-bold text-sm transition-colors flex items-center tracking-widest">
                <LineChart size={16} className="mr-2" /> CHART
              </button>
              <button className="text-text-secondary hover:text-text-primary font-bold text-sm transition-colors flex items-center tracking-widest">
                <Settings size={16} className="mr-2" /> SETTING
              </button>
            </nav>

            <button 
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="p-2 text-text-secondary hover:text-text-primary bg-bg-surface border border-border rounded-lg transition-colors"
              title="Toggle Theme"
            >
              {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>
            
            <div className="h-8 w-px bg-border"></div>
            
            {/* LOGIN INFORMATION */}
            <div className="flex items-center space-x-3 cursor-pointer hover:opacity-80 transition-opacity">
              <div className="text-right hidden sm:block">
                <div className="text-sm font-bold text-text-primary">ADMINISTRATOR</div>
                <div className="text-xs text-text-secondary font-mono">ID: OP-7729</div>
              </div>
              <div className="h-10 w-10 bg-bg-surface border border-border rounded-full flex items-center justify-center overflow-hidden">
                <User size={20} className="text-text-secondary" />
              </div>
            </div>
          </div>
        </header>
      )}

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 relative overflow-hidden bg-bg-base flex">
        
        {/* MAP/DIAGRAM VISUALIZATION (Background Layer) */}
        <div className="flex-1 relative flex bg-bg-panel/30 overflow-hidden">
          {viewMode === 'satellite' ? (
            <div className="w-full h-full relative z-0">
              <MapContainer 
                bounds={[
                  [-0.3076283024687055, 115.85749409146369],
                  [-0.29970261465644, 115.86817796519595]
                ]}
                minZoom={14}
                maxZoom={20}
                maxBounds={[
                  [-0.315000, 115.845000],
                  [-0.290000, 115.880000]
                ]}
                maxBoundsViscosity={1.0}
                className="w-full h-full"
                zoomControl={false}
              >
                <MapController isFullscreen={isFullscreen} />
                
                {/* GOOGLE SATELLITE TILE SERVER */}
                <TileLayer
                  url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
                  attribution="&copy; Google Maps"
                />
                
                {/* DUMMY FIBER OPTIC LINE (South West to North East) */}
                <Polyline 
                  positions={[
                    [-0.3076283024687055, 115.85749409146369], // SW
                    [-0.29970261465644, 115.86817796519595]  // NE
                  ]} 
                  pathOptions={{ color: '#43b581', weight: 4 }}
                >
                  <Tooltip sticky>FO Line - Conveyor Main</Tooltip>
                </Polyline>

                {/* DUMMY ALARM SEGMENT (Pulsing Red) */}
                <Polyline 
                  positions={[
                    [-0.304457, 115.861767],
                    [-0.303665, 115.862835]
                  ]} 
                  pathOptions={{ color: '#f04747', weight: 6, className: 'animate-pulse' }}
                >
                  <Tooltip sticky>Overheat Detected: 84.2°C</Tooltip>
                </Polyline>

              </MapContainer>
            </div>
          ) : (            <div className="w-full h-full bg-bg-panel flex flex-col relative overflow-hidden custom-scrollbar p-6">
              
              {/* HEADER P&ID */}
              <div className={`flex justify-between items-center mb-4 shrink-0 bg-bg-surface p-4 rounded-xl border border-border shadow-lg z-10 ${!isFullscreen ? 'ml-[400px]' : ''}`}>
                <div className="flex items-center">
                  <Layout className="text-scada-primary mr-3" size={24} />
                  <div>
                    <h2 className="text-text-primary font-bold tracking-widest text-lg">DTS SCHEMATIC VIEW</h2>
                    <p className="text-text-secondary text-xs font-mono">DISTRIBUTED TEMPERATURE SENSING</p>
                  </div>
                </div>
              </div>

              {/* SVG CANVAS */}
              <div className={`flex-1 bg-bg-base border border-border rounded-xl overflow-auto custom-scrollbar relative shadow-scada-inset flex items-center justify-center ${!isFullscreen ? 'pl-[400px]' : ''}`}>
                <svg viewBox="0 0 1450 600" className="w-[1600px] h-[660px] min-w-[1200px] drop-shadow-2xl -translate-y-8">
                  
                  <defs>
                    <pattern id="dotGrid" width="30" height="30" patternUnits="userSpaceOnUse">
                      <circle cx="2" cy="2" r="1" className="fill-border" />
                    </pattern>
                  </defs>
                  
                  <rect width="100%" height="100%" fill="url(#dotGrid)" />

                  {/* ==================== ASSETS (CONVEYORS & NODES) ==================== */}
                  
                  {/* C1 (Left Main Conveyor - 500m) */}
                  <rect x="40" y="290" width="500" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
                  <text x="290" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="3">BC MAIN - 01 (500m)</text>

                  {/* C2 (Right Main Conveyor - 800m) */}
                  <rect x="600" y="290" width="800" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
                  <text x="1000" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="3">BC MAIN - 02 (800m)</text>

                  {/* ==================== ASSETS (CONVEYORS & NODES) ==================== */}
                  
                  {/* C1 (Left Main Conveyor - 500m) */}
                  <rect x="40" y="290" width="500" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
                  <text x="290" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="3">BC MAIN - 01 (500m)</text>

                  {/* C2 (Right Main Conveyor - 800m) */}
                  <rect x="600" y="290" width="800" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
                  <text x="1000" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="3">BC MAIN - 02 (800m)</text>

                  {/* Top Nodes (TF Conveyor Tunnels - 70m length, Aligned) */}
                  {[
                    { id: 1, x: 140 },
                    { id: 2, x: 240 },
                    { id: 3, x: 340 },
                    { id: 4, x: 440 }
                  ].map(node => (
                    <g key={`TF${node.id}`} transform={`translate(${node.x}, 170)`}>
                      <rect width="20" height="70" className="fill-bg-surface stroke-border" strokeWidth="2" rx="3" />
                      <text x="10" y="-12" className="fill-text-secondary" fontSize="11" fontWeight="bold" textAnchor="middle">TF-{node.id}</text>
                    </g>
                  ))}

                  {/* Bottom Nodes (BF Conveyor Tunnels - 30m length, Aligned) */}
                  {[
                    { id: 1, x: 110 },
                    { id: 2, x: 180 },
                    { id: 3, x: 250 },
                    { id: 4, x: 320 },
                    { id: 5, x: 390 },
                    { id: 6, x: 460 }
                  ].map(node => (
                    <g key={`BF${node.id}`} transform={`translate(${node.x}, 340)`}>
                      <rect width="20" height="30" className="fill-bg-surface stroke-border" strokeWidth="2" rx="3" />
                      <text x="10" y="48" className="fill-text-secondary" fontSize="11" fontWeight="bold" textAnchor="middle">BF-{node.id}</text>
                    </g>
                  ))}

                  {/* Control Room */}
                  <g transform="translate(520, 430)">
                    <rect width="100" height="60" className="fill-bg-panel stroke-border" strokeWidth="2" rx="8" />
                    <text x="50" y="27" className="fill-scada-accent" fontSize="11" fontWeight="bold" textAnchor="middle">CONTROL</text>
                    <text x="50" y="42" className="fill-scada-accent" fontSize="11" fontWeight="bold" textAnchor="middle">ROOM</text>
                    <circle cx="10" cy="10" r="3" className="fill-scada-success animate-pulse" />
                  </g>


                  {/* ==================== EXACT FIBER OPTIC ROUTES (DENAH-2) ==================== */}
                  
                  {/* HORIZONTAL CABLE TRAYS */}
                  
                  {/* H6: Bottom-most line above BC1 */}
                  <path d="M 40 280 L 540 280" stroke="#22c55e" strokeWidth="3" fill="none" />
                  
                  {/* H1: Middle line above BC1 (connects TF1/TF2 jumpers) */}
                  <path d="M 40 270 L 540 270" stroke="#22c55e" strokeWidth="3" fill="none" />
                  
                  {/* H2: Top line above BC1 (connects TF3/TF4 jumpers) */}
                  <path d="M 360 260 L 540 260" stroke="#22c55e" strokeWidth="3" fill="none" />
                  
                  {/* H3: Below Left Conveyor */}
                  <path d="M 40 325 L 200 325" stroke="#22c55e" strokeWidth="3" fill="none" />
                  
                  {/* ALARM SEGMENT ON H3 WITH HOVER BADGE */}
                  <g className="group cursor-pointer">
                    <path d="M 200 325 L 350 325" stroke="transparent" strokeWidth="20" fill="none" />
                    <path d="M 200 325 L 350 325" stroke="#ef4444" strokeWidth="4" fill="none" className="animate-pulse" />
                    <foreignObject x="245" y="295" width="55" height="24" className="opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                      <div className="bg-red-950 border border-red-500 rounded flex items-center justify-center shadow-[0_0_15px_rgba(239,68,68,0.4)] h-full">
                        <span className="text-red-400 text-[10px] font-mono font-bold animate-pulse">84.2°C</span>
                      </div>
                    </foreignObject>
                  </g>
                  <path d="M 350 325 L 540 325" stroke="#22c55e" strokeWidth="3" fill="none" />

                  {/* BC2 H4 with NORMAL HOVER BADGE */}
                  <g className="group cursor-pointer">
                    <path d="M 600 325 L 1400 325" stroke="transparent" strokeWidth="20" fill="none" />
                    <path d="M 600 325 L 1400 325" stroke="#22c55e" strokeWidth="3" fill="none" />
                    <foreignObject x="1000" y="295" width="55" height="24" className="opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                      <div className="bg-bg-surface border border-border rounded flex items-center justify-center h-full shadow-lg">
                        <span className="text-scada-success text-[10px] font-mono font-bold">34.5°C</span>
                      </div>
                    </foreignObject>
                  </g>

                  {/* H5: Above BC2 */}
                  <path d="M 800 275 L 1100 275" stroke="#22c55e" strokeWidth="3" fill="none" />


                  {/* VERTICAL FO SENSING CABLES (ON SIDE OF CONVEYORS) */}
                  
                  {/* TF1 */}
                  <path d="M 160 170 L 160 270" stroke="#22c55e" strokeWidth="2" fill="none" />
                  
                  {/* TF2 */}
                  <path d="M 260 170 L 260 270" stroke="#22c55e" strokeWidth="2" fill="none" />
                  
                  {/* TF3 with NORMAL HOVER BADGE */}
                  <g className="group cursor-pointer">
                    <path d="M 360 170 L 360 260" stroke="transparent" strokeWidth="20" fill="none" />
                    <path d="M 360 170 L 360 260" stroke="#22c55e" strokeWidth="2" fill="none" />
                    <foreignObject x="375" y="195" width="55" height="24" className="opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                      <div className="bg-bg-surface border border-border rounded flex items-center justify-center h-full shadow-lg">
                        <span className="text-scada-success text-[10px] font-mono font-bold">32.1°C</span>
                      </div>
                    </foreignObject>
                  </g>

                  {/* TF4 */}
                  <path d="M 460 170 L 460 260" stroke="#22c55e" strokeWidth="2" fill="none" />

                  {/* Bottom 6 Feeders */}
                  {[
                    { id: 1, x: 130, isAlarm: false },
                    { id: 2, x: 200, isAlarm: false },
                    { id: 3, x: 270, isAlarm: true }, // Taps near alarm zone
                    { id: 4, x: 340, isAlarm: true }, // Taps near alarm zone
                    { id: 5, x: 410, isAlarm: false },
                    { id: 6, x: 480, isAlarm: false }
                  ].map(v => (
                    <g key={`VBF${v.id}`}>
                      {/* FO Sensing Cable directly connecting to H3 */}
                      <path 
                        d={`M ${v.x} 325 L ${v.x} 370`} 
                        stroke={v.isAlarm ? "#ef4444" : "#22c55e"} 
                        strokeWidth={v.isAlarm ? 3 : 2} 
                        fill="none" 
                        className={v.isAlarm ? "animate-pulse" : ""} 
                      />
                    </g>
                  ))}

                </svg>
              </div>
            </div>
          )}

          {/* View Toolbar overlay (Right) */}
          <div className="absolute top-4 right-4 z-20 flex flex-col space-y-2">
            <div className="flex flex-col bg-bg-panel/80 backdrop-blur border border-border rounded-lg shadow-xl overflow-hidden">
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
              className="p-3 bg-bg-panel/80 hover:bg-bg-panel border border-border text-text-primary rounded-lg transition-colors backdrop-blur shadow-xl flex items-center justify-center mt-2"
              title="Toggle Fullscreen"
            >
              {isFullscreen ? <Minimize2 size={20} /> : <Maximize2 size={20} />}
            </button>
          </div>
        </div>

        {/* GLOBAL LEGEND (Bottom Left) */}
        <div className="absolute bottom-4 left-4 z-30 w-96 bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl shadow-lg p-3 pointer-events-auto transition-all duration-300 flex flex-col space-y-2">
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

        {/* BOTTOM RIGHT FLOATING CONTAINER */}
        <div className="absolute bottom-4 right-4 z-30 flex flex-col space-y-4 w-96 pointer-events-none">
          
          {/* SYSTEM LOGS */}
          <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl p-4 shadow-lg pointer-events-auto flex flex-col">
            <div className="text-sm font-bold text-text-primary uppercase tracking-widest flex items-center border-b border-border pb-2 mb-3 shrink-0">
              <History size={16} className="mr-2 text-scada-primary" /> SYSTEM LOGS
            </div>
            <div className="flex flex-col space-y-2 overflow-y-auto custom-scrollbar max-h-[200px] pr-1">
              {dummyLogs.map(log => (
                <div key={log.id} className="flex flex-col bg-bg-surface p-2.5 rounded-lg border border-border shadow-sm shrink-0">
                  <div className="flex justify-between items-center mb-1.5">
                    <span className="text-[10px] font-mono text-text-secondary bg-bg-base px-1.5 py-0.5 rounded border border-border">{log.time}</span>
                    <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${log.type === 'error' ? 'bg-red-500/20 text-red-400' : log.type === 'warn' ? 'bg-yellow-500/20 text-yellow-500' : 'bg-scada-primary/20 text-scada-primary'}`}>
                      {log.type}
                    </span>
                  </div>
                  <p className="text-xs text-text-primary line-clamp-2 leading-relaxed">{log.msg}</p>
                </div>
              ))}
            </div>
          </div>

          {/* SYSTEM STATUS & TIME */}
          <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl shadow-lg p-3 pointer-events-auto transition-all duration-300 flex items-center justify-between">
            <div className="flex flex-col items-start pl-2">
              <span className="text-[10px] text-text-secondary uppercase font-bold tracking-widest">DTS Connection</span>
              <div className="flex items-center text-scada-success font-bold text-xs mt-1">
                <Wifi size={14} className="mr-1 animate-pulse" />
                ONLINE (MySQL)
              </div>
            </div>
            
            <div className="h-8 w-px bg-border"></div>
            
            <div className="flex flex-col items-end min-w-[120px] pr-2">
              <span className="text-[10px] font-bold text-text-secondary font-mono tracking-widest uppercase">
                {currentTime.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })}
              </span>
              <div className="flex items-center text-scada-primary font-mono font-bold text-base mt-0.5">
                <Clock size={14} className="mr-1.5" />
                {currentTime.toLocaleTimeString('en-GB', { hour12: false })}
              </div>
            </div>
          </div>
        </div>

        {/* FLOATING LEFT PANEL - AREA LIST */}
        {!isFullscreen && (
          <aside className="absolute top-4 left-4 bottom-[90px] w-96 flex flex-col z-20 pointer-events-none space-y-4">
            
            {/* 1. AREA MONITORING & GRID (4 items) */}
            <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl p-4 shadow-lg pointer-events-auto flex flex-col shrink-0">
              <div className="text-sm font-bold text-text-primary uppercase tracking-widest flex items-center mb-3">
                <MapPin size={16} className="mr-2 text-scada-primary" />
                AREA MONITORING
              </div>
              
              {/* SEARCH / FILTER INPUT */}
              <div className="relative mb-3">
                <Search size={14} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-secondary" />
                <input 
                  type="text" 
                  placeholder="Search area..." 
                  value={searchTerm}
                  onChange={e => { setSearchTerm(e.target.value); setCurrentPage(1); }}
                  className="w-full bg-bg-surface border border-border rounded-lg pl-9 pr-3 py-2 text-sm text-text-primary placeholder-gray-500 focus:outline-none focus:border-scada-primary transition-colors"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                {Array.from({ length: 4 }).map((_, idx) => {
                  const area = currentAreas[idx];
                  if (!area) {
                    return (
                      <div key={`empty-${idx}`} className="p-3 rounded-xl flex flex-col border border-transparent opacity-0 pointer-events-none">
                        <div className="flex justify-between items-start mb-2"><span className="font-bold text-base">&nbsp;</span></div>
                        <div className="flex justify-between items-end mt-auto pt-2"><span className="text-sm font-semibold">&nbsp;</span><span className="text-base font-mono font-bold">&nbsp;</span></div>
                      </div>
                    );
                  }
                  return (
                    <div 
                      key={area.id} 
                      className={`p-3 rounded-xl flex flex-col cursor-pointer transition-all hover:-translate-y-1 shadow-lg backdrop-blur-md border
                        ${area.isAlarm 
                          ? 'bg-bg-alarm/95 border-red-500 shadow-[0_0_15px_rgba(240,71,71,0.3)]' 
                          : 'bg-bg-panel/95 border-border hover:bg-bg-surface'}`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <span className={`font-bold text-base drop-shadow-md ${area.isAlarm ? 'text-red-400' : 'text-text-primary'}`}>
                          {area.name}
                        </span>
                        {area.isAlarm && <AlertTriangle size={14} className="text-scada-alert animate-pulse" />}
                      </div>
                      <div className="flex justify-between items-end mt-auto pt-2">
                        <span className="text-sm font-semibold text-text-primary drop-shadow-md">
                          {area.distance}
                        </span>
                        <span className={`text-base font-mono font-bold drop-shadow-md ${area.isAlarm ? 'text-red-400' : 'text-scada-success'}`}>
                          {area.temp}°C
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
              
              {/* PAGINATION & VIEW ALL BUTTON */}
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-border">
                <div className="flex items-center space-x-1.5">
                  {totalPages > 1 && Array.from({ length: totalPages }).map((_, idx) => (
                    <button 
                      key={idx}
                      onClick={() => setCurrentPage(idx + 1)}
                      className={`h-1.5 rounded-full transition-all ${currentPage === idx + 1 ? 'bg-scada-primary w-4' : 'bg-border hover:bg-text-secondary w-1.5'}`}
                      title={`Page ${idx + 1}`}
                    />
                  ))}
                </div>
                <button 
                  onClick={() => setShowDataModal(true)}
                  className="text-xs font-bold text-text-secondary hover:text-scada-primary transition-colors flex items-center uppercase tracking-wider"
                >
                  <List size={14} className="mr-1" /> View All
                </button>
              </div>
            </div>

            {/* 2. SYSTEM STATISTICS */}
            <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl p-4 shadow-lg pointer-events-auto shrink-0 flex flex-col">
               <div className="text-sm font-bold text-text-primary uppercase tracking-widest flex items-center border-b border-border pb-2 mb-3">
                 <Activity size={16} className="mr-2 text-scada-primary" /> SEGMENT STATS
               </div>
               <div className="grid grid-cols-4 gap-2 text-center">
                 <div className="flex flex-col bg-bg-surface p-2 rounded border border-border">
                   <span className="text-lg font-mono font-bold text-text-primary">{totalSegments}</span>
                   <span className="text-[9px] text-text-secondary uppercase font-bold tracking-widest mt-1">Total</span>
                 </div>
                 <div className="flex flex-col bg-bg-surface p-2 rounded border border-border">
                   <span className="text-lg font-mono font-bold text-scada-success">{normalSegments}</span>
                   <span className="text-[9px] text-text-secondary uppercase font-bold tracking-widest mt-1">Normal</span>
                 </div>
                 <div className="flex flex-col bg-bg-surface p-2 rounded border border-border">
                   <span className="text-lg font-mono font-bold text-yellow-500">{warningSegments}</span>
                   <span className="text-[9px] text-text-secondary uppercase font-bold tracking-widest mt-1">Warn</span>
                 </div>
                 <div className="flex flex-col bg-bg-alarm/50 p-2 rounded border border-red-500/30">
                   <span className="text-lg font-mono font-bold text-red-500">{dangerSegments}</span>
                   <span className="text-[9px] text-red-400 uppercase font-bold tracking-widest mt-1">Danger</span>
                 </div>
               </div>
            </div>

            {/* 3. TEMPERATURE CHART */}
            <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl p-4 shadow-lg pointer-events-auto flex-1 flex flex-col min-h-0">
               <div className="text-sm font-bold text-text-primary uppercase tracking-widest flex items-center border-b border-border pb-2 mb-3 shrink-0">
                 <LineChart size={16} className="mr-2 text-scada-primary" /> TEMPERATURE TREND
               </div>
               <div className="flex-1 w-full min-h-0">
                 <ResponsiveContainer width="100%" height="100%">
                   <RechartsLineChart data={dummyChartData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                     <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" opacity={0.3} />
                     <XAxis dataKey="time" stroke="#9ca3af" fontSize={10} tickMargin={5} />
                     <YAxis stroke="#9ca3af" fontSize={10} />
                     <RechartsTooltip 
                       contentStyle={{ backgroundColor: 'var(--bg-panel)', borderColor: 'var(--border-color)', borderRadius: '8px', fontSize: '12px' }}
                       itemStyle={{ color: '#06b6d4', fontWeight: 'bold' }}
                       labelStyle={{ color: 'var(--text-secondary)' }}
                     />
                     <Line type="monotone" dataKey="temp" stroke="#06b6d4" strokeWidth={2} dot={{ r: 3, fill: '#06b6d4', strokeWidth: 0 }} activeDot={{ r: 5, strokeWidth: 0 }} />
                   </RechartsLineChart>
                 </ResponsiveContainer>
               </div>
            </div>
          </aside>
        )}

        {/* FULLSCREEN DATA MODAL */}
        {showDataModal && (
          <div className="absolute inset-0 z-50 flex flex-col bg-bg-base/95 backdrop-blur-md p-8 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex justify-between items-center mb-6">
              <div className="flex items-center">
                <List className="text-scada-primary mr-3" size={28} />
                <div>
                  <h2 className="text-text-primary font-bold tracking-widest text-2xl uppercase">COMPLETE SEGMENT DATA</h2>
                  <p className="text-text-secondary font-mono text-sm">ALL FIBER OPTIC POINTS MONITORING</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                {/* View Mode Toggle */}
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
                      {areas.map((area, idx) => (
                        <tr key={area.id} className={`hover:bg-white/[0.02] transition-colors ${area.isAlarm ? 'bg-red-950/20' : ''}`}>
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
                    {areas.map(area => (
                      <div 
                        key={area.id} 
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

      </div>
    </div>
  );
}
