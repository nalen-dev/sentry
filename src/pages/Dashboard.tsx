import { useState } from 'react';
import { Activity, Map, Image as ImageIcon, Settings, AlertTriangle, ActivitySquare } from 'lucide-react';

export default function Dashboard() {
  const [viewMode, setViewMode] = useState<'satellite' | 'diagram'>('diagram');

  return (
    <div className="h-screen bg-scada-dark flex flex-col text-scada-text overflow-hidden">
      {/* HEADER / TOP BAR */}
      <header className="h-16 bg-scada-panel border-b border-scada-border flex items-center justify-between px-6 shrink-0">
        <div className="flex items-center space-x-3">
          <Activity className="text-scada-primary" />
          <h1 className="text-xl font-bold text-white tracking-widest">DTS SYSTEM</h1>
        </div>
        
        {/* SUMMARY STATS */}
        <div className="flex space-x-6">
          <div className="flex flex-col items-end">
            <span className="text-xs text-gray-400">Max Temp</span>
            <span className="text-lg font-mono font-bold text-scada-alert">84.2 °C</span>
          </div>
          <div className="flex flex-col items-end">
            <span className="text-xs text-gray-400">Avg Temp</span>
            <span className="text-lg font-mono font-bold text-scada-accent">32.1 °C</span>
          </div>
          <div className="flex flex-col items-end">
            <span className="text-xs text-gray-400">System Status</span>
            <span className="text-lg font-bold text-scada-accent">NORMAL</span>
          </div>
        </div>
      </header>

      {/* MAIN LAYOUT */}
      <div className="flex flex-1 overflow-hidden">
        {/* LEFT SIDEBAR - MENU */}
        <aside className="w-16 bg-scada-panel border-r border-scada-border flex flex-col items-center py-4 space-y-6 shrink-0">
          <button 
            onClick={() => setViewMode('diagram')}
            className={`p-3 rounded-xl transition-all ${viewMode === 'diagram' ? 'bg-scada-primary text-white shadow-lg' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
            title="Diagram View"
          >
            <ImageIcon size={24} />
          </button>
          <button 
            onClick={() => setViewMode('satellite')}
            className={`p-3 rounded-xl transition-all ${viewMode === 'satellite' ? 'bg-scada-primary text-white shadow-lg' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}
            title="Satellite Map View"
          >
            <Map size={24} />
          </button>
          <button className="p-3 text-gray-400 hover:text-white hover:bg-white/5 rounded-xl transition-all" title="Temperature Graphs">
            <ActivitySquare size={24} />
          </button>
          <button className="p-3 text-gray-400 hover:text-white hover:bg-white/5 rounded-xl transition-all mt-auto" title="Settings">
            <Settings size={24} />
          </button>
        </aside>

        {/* CENTER - VISUALIZATION */}
        <main className="flex-1 relative bg-black flex flex-col">
          <div className="absolute top-4 left-4 z-10 bg-scada-panel/80 backdrop-blur border border-scada-border px-4 py-2 rounded text-sm font-semibold text-white shadow-xl">
            {viewMode === 'satellite' ? 'SATELLITE VIEW (Leaflet)' : 'DIAGRAM VIEW (Reference)'}
          </div>
          
          {/* Placeholder for the actual map or diagram */}
          <div className="flex-1 flex items-center justify-center border-4 border-dashed border-scada-border m-4 rounded-xl opacity-50">
            {viewMode === 'satellite' ? (
              <span className="text-gray-500 font-mono">[ React-Leaflet Map Container will go here ]</span>
            ) : (
              <span className="text-gray-500 font-mono">[ Static Diagram Image with Overlaid Polylines will go here ]</span>
            )}
          </div>
        </main>

        {/* RIGHT SIDEBAR - ALARM LOG */}
        <aside className="w-80 bg-scada-panel border-l border-scada-border flex flex-col shrink-0">
          <div className="p-4 border-b border-scada-border flex items-center justify-between bg-black/20">
            <h2 className="font-semibold text-white flex items-center">
              <AlertTriangle size={18} className="text-scada-alert mr-2" />
              ALARM HISTORY
            </h2>
            <span className="bg-scada-alert/20 text-scada-alert text-xs px-2 py-1 rounded font-bold">2 NEW</span>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {/* Dummy Alarms */}
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className={`p-3 rounded border ${i <= 2 ? 'bg-scada-alert/10 border-scada-alert/50' : 'bg-black/20 border-scada-border'}`}>
                <div className="flex justify-between items-start mb-1">
                  <span className={`font-bold text-sm ${i <= 2 ? 'text-scada-alert' : 'text-gray-300'}`}>Segment A-{i}</span>
                  <span className="text-xs text-gray-500">10:42 AM</span>
                </div>
                <p className="text-xs text-gray-400">Temperature exceeded threshold ({i <= 2 ? '84.2' : '45.1'}°C)</p>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}
