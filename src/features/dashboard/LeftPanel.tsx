import { Search, MapPin, AlertTriangle, List, ChevronLeft, ChevronRight } from 'lucide-react';
import { SegmentData } from '../../components/SegmentDetailModal';

interface LeftPanelProps {
  isFullscreen: boolean;
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  setCurrentPage: (page: number) => void;
  currentAreas: SegmentData[];
  setSelectedSegment: (segment: SegmentData) => void;
  totalPages: number;
  currentPage: number;
  setShowDataModal: (show: boolean) => void;
  
  // Grouping Props
  mainGroups: string[];
  activeMainGroup: string;
  setActiveMainGroup: (g: string) => void;
  subGroups: string[];
  activeSubGroup: string;
  setActiveSubGroup: (g: string) => void;
}

export default function LeftPanel({
  isFullscreen,
  searchTerm,
  setSearchTerm,
  setCurrentPage,
  currentAreas,
  setSelectedSegment,
  totalPages,
  currentPage,
  setShowDataModal,
  mainGroups,
  activeMainGroup,
  setActiveMainGroup,
  subGroups,
  activeSubGroup,
  setActiveSubGroup
}: LeftPanelProps) {
  return (
    <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl p-4 shadow-lg pointer-events-auto flex flex-col shrink-0">
      <div className="text-sm font-bold text-text-primary uppercase tracking-widest flex items-center mb-3">
        <MapPin size={16} className="mr-2 text-scada-primary" />
        AREA MONITORING
      </div>
      
      {!isFullscreen && (
        <div className="flex flex-col space-y-2 mb-3">
          <div className="flex space-x-2">
            <select 
              value={activeMainGroup} 
              onChange={e => { setActiveMainGroup(e.target.value); setActiveSubGroup('All'); setCurrentPage(1); }}
              className="w-1/2 bg-bg-surface border border-border rounded-lg p-2 text-xs text-text-primary focus:outline-none focus:border-scada-primary cursor-pointer font-bold"
            >
              <option value="All">All Areas</option>
              {mainGroups.map(g => <option key={g} value={g}>{g}</option>)}
            </select>
            
            <select 
              value={activeSubGroup} 
              onChange={e => { setActiveSubGroup(e.target.value); setCurrentPage(1); }}
              disabled={activeMainGroup === 'All' || subGroups.length === 0}
              className="w-1/2 bg-bg-surface border border-border rounded-lg p-2 text-xs text-text-primary focus:outline-none focus:border-scada-primary cursor-pointer font-bold disabled:opacity-50"
            >
              <option value="All">All Subgroups</option>
              {subGroups.map(g => <option key={g} value={g}>{g}</option>)}
            </select>
          </div>

          <div className="relative">
            <Search size={14} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-text-secondary" />
            <input 
              type="text" 
              placeholder="Search segment..." 
              value={searchTerm}
              onChange={e => { setSearchTerm(e.target.value); setCurrentPage(1); }}
              className="w-full bg-bg-surface border border-border rounded-lg pl-9 pr-3 py-2 text-sm text-text-primary placeholder-gray-500 focus:outline-none focus:border-scada-primary transition-colors"
            />
          </div>
        </div>
      )}

      <div className={`grid ${isFullscreen ? 'grid-cols-1' : 'grid-cols-2'} gap-2`}>
        {Array.from({ length: isFullscreen ? 2 : 4 }).map((_, idx) => {
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
              onClick={() => setSelectedSegment(area)}
              className={`p-3 rounded-xl flex flex-col cursor-pointer transition-all hover:-translate-y-1 shadow-lg backdrop-blur-md border
                ${area.isAlarm 
                  ? 'bg-bg-alarm/95 border-red-500 shadow-[0_0_15px_rgba(240,71,71,0.3)]' 
                  : 'bg-bg-panel/95 border-border hover:bg-bg-surface'}`}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex flex-col">
                  <span className={`font-bold text-base drop-shadow-md ${area.isAlarm ? 'text-red-400' : 'text-text-primary'}`}>
                    {area.name}
                  </span>
                  {area.isAlarm && (
                    <span className="text-[10px] font-bold font-mono tracking-wider mt-1 px-2 py-0.5 rounded bg-red-500/20 text-red-400 w-fit">
                      {area.status}
                    </span>
                  )}
                </div>
                {area.isAlarm && <AlertTriangle size={14} className="text-scada-alert animate-pulse shrink-0" />}
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
      
      <div className="flex items-center justify-between mt-3 pt-3 border-t border-border">
        <div className="flex items-center space-x-2">
          <button 
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
            className="p-1 rounded bg-bg-surface text-text-secondary hover:text-scada-primary disabled:opacity-30 disabled:hover:text-text-secondary transition-colors"
          >
            <ChevronLeft size={16} />
          </button>
          <span className="text-xs font-mono font-bold text-text-secondary">
            {currentPage} / {Math.max(1, totalPages)}
          </span>
          <button 
            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage >= totalPages}
            className="p-1 rounded bg-bg-surface text-text-secondary hover:text-scada-primary disabled:opacity-30 disabled:hover:text-text-secondary transition-colors"
          >
            <ChevronRight size={16} />
          </button>
        </div>
        <button 
          onClick={() => setShowDataModal(true)}
          className="text-xs font-bold text-text-secondary hover:text-scada-primary transition-colors flex items-center uppercase tracking-wider"
        >
          <List size={14} className="mr-1" /> View All
        </button>
      </div>
    </div>
  );
}
