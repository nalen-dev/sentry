import { Layout } from 'lucide-react';
import { DUMMY_AREAS } from '../../data/constants';

export default function DiagramVisualization({ isFullscreen }: { isFullscreen: boolean }) {
  const getStrokeClass = (areaId: string) => {
    const area = DUMMY_AREAS.find(a => a.id === areaId);
    if (!area) return 'stroke-border';
    if (area.isAlarm) return 'stroke-red-500 animate-pulse drop-shadow-[0_0_8px_rgba(239,68,68,0.8)]';
    if (parseFloat(area.temp) >= 45) return 'stroke-yellow-500';
    return 'stroke-scada-primary';
  };

  return (
    <div className="w-full h-full bg-bg-panel flex flex-col relative overflow-hidden custom-scrollbar p-6">
      
      {/* HEADER P&ID */}
      <div className={`flex justify-between items-center mb-4 shrink-0 bg-bg-surface p-4 rounded-xl border border-border shadow-lg z-10 ${!isFullscreen ? 'ml-[400px]' : ''} transition-all duration-500`}>
        <div className="flex items-center">
          <Layout className="text-scada-primary mr-3" size={24} />
          <div>
            <h2 className="text-text-primary font-bold tracking-widest text-lg">DTS SCHEMATIC VIEW</h2>
            <p className="text-text-secondary text-xs font-mono">DISTRIBUTED TEMPERATURE SENSING</p>
          </div>
        </div>
      </div>

      {/* SVG CANVAS */}
      <div className={`flex-1 bg-bg-base border border-border rounded-xl overflow-auto custom-scrollbar relative shadow-scada-inset flex items-center justify-center ${!isFullscreen ? 'pl-[400px]' : ''} transition-all duration-500`}>
        <svg viewBox="0 0 1450 600" className="w-[1600px] h-[660px] min-w-[1200px] drop-shadow-2xl -translate-y-8">
          
          <defs>
            <pattern id="dotGrid" width="30" height="30" patternUnits="userSpaceOnUse">
              <circle cx="2" cy="2" r="1" className="fill-border" />
            </pattern>
          </defs>
          
          <rect width="100%" height="100%" fill="url(#dotGrid)" />

          {/* C1 (Left Main Conveyor - 500m) */}
          <rect x="40" y="290" width="635" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
          <text x="357" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="3">BC MAIN - 01 (500m)</text>

          {/* C2 (Right Main Conveyor - 800m) */}
          <rect x="675" y="290" width="705" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
          <text x="1027" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="3">BC MAIN - 02 (800m)</text>

          {/* Top Nodes (TN BEK 3 - 6, Staggered) */}
          {[
            { id: 'TN BEK 3', x: 290 },
            { id: 'TN BEK 4', x: 390 },
            { id: 'TN BEK 5', x: 490 },
            { id: 'TN BEK 6', x: 590 } // Rightmost node!
          ].map((node, i) => (
            <g key={`TF${i}`} transform={`translate(${node.x}, 220)`}>
              <rect width="20" height="50" className="fill-bg-surface stroke-border" strokeWidth="2" rx="3" />
              <text x="10" y="-12" className="fill-text-secondary" fontSize="11" fontWeight="bold" textAnchor="middle">{node.id}</text>
            </g>
          ))}

          {/* Bottom Nodes (TN TCM 1 - 6) */}
          {[
            { id: 'TN TCM 1', x: 40 },
            { id: 'TN TCM 2', x: 140 },
            { id: 'TN TCM 3', x: 240 },
            { id: 'TN TCM 4', x: 340 },
            { id: 'TN TCM 5', x: 440 },
            { id: 'TN TCM 6', x: 540 }
          ].map((node, i) => (
            <g key={`BF${i}`} transform={`translate(${node.x}, 332)`}>
              <rect width="20" height="40" className="fill-bg-surface stroke-border" strokeWidth="2" rx="3" />
              <text x="10" y="64" className="fill-text-secondary" fontSize="11" fontWeight="bold" textAnchor="middle">{node.id}</text>
            </g>
          ))}

          {/* SENSING FIBER ROUTES */}
          
          {/* FIBER B (TN BEK 3, TN BEK 4) -> FO B (Warning) */}
          <path d="M 315,220 L 315,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 415,220 L 415,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 315,282 L 661,282" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 661,282 L 661,400" fill="none" strokeWidth="3" strokeDasharray="5,5" className={getStrokeClass("A-3")} />
          
          {/* FIBER A (TN BEK 5, TN BEK 6) -> FO A (Normal) */}
          <path d="M 515,220 L 515,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 615,220 L 615,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 515,274 L 689,274" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 689,274 L 689,400" fill="none" strokeWidth="3" strokeDasharray="5,5" className={getStrokeClass("A-2")} />
          
          {/* FIBER C (Full Length Top - BC 01, Dashed crossing) */}
          <path d="M 50,290 L 668,290" fill="none" strokeWidth="3" className={getStrokeClass("A-1")} />
          <path d="M 668,290 L 668,400" fill="none" strokeWidth="3" strokeDasharray="5,5" className={getStrokeClass("A-1")} />
          
          {/* FIBER D (Bottom Tunnels TN TCM 1-6) */}
          <path d="M 65,372 L 65,322" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 165,372 L 165,322" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 265,372 L 265,322" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 365,372 L 365,322" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 465,372 L 465,322" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 565,372 L 565,322" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          
          <path d="M 65,322 L 675,322" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 675,322 L 675,400" fill="none" strokeWidth="3" strokeDasharray="5,5" className={getStrokeClass("A-4")} />

          {/* MAIN TRUNK ROUTE BC MAIN 02 */}
          <path d="M 682,314 L 1380,314" fill="none" strokeWidth="3" className={getStrokeClass("A-10")} />
          <path d="M 682,314 L 682,400" fill="none" strokeWidth="3" strokeDasharray="5,5" className={getStrokeClass("A-10")} />

          {/* SYSTEM CONTROL ROOM (Bigger, Lowered) */}
          <g transform="translate(635, 360)">
            <rect x="0" y="0" width="80" height="80" className="fill-bg-panel stroke-border" strokeWidth="2" rx="6" />
            <circle cx="40" cy="40" r="14" className="fill-bg-surface stroke-scada-primary" strokeWidth="3" />
            <text x="40" y="100" className="fill-text-primary" fontSize="11" fontWeight="bold" textAnchor="middle">CONTROL</text>
            <text x="40" y="114" className="fill-text-primary" fontSize="11" fontWeight="bold" textAnchor="middle">ROOM</text>
          </g>
        </svg>
      </div>
    </div>
  );
}
