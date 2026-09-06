import { Search, MapPin, AlertTriangle, List } from 'lucide-react';
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
  setShowDataModal
}: LeftPanelProps) {
  return (
    <div className="bg-bg-panel/95 backdrop-blur-md border border-border rounded-xl p-4 shadow-lg pointer-events-auto flex flex-col shrink-0">
      <div className="text-sm font-bold text-text-primary uppercase tracking-widest flex items-center mb-3">
        <MapPin size={16} className="mr-2 text-scada-primary" />
        AREA MONITORING
      </div>
      
      {!isFullscreen && (
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
  );
}
