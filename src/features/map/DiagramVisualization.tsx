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
          <rect x="40" y="290" width="500" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
          <text x="290" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="3">BC MAIN - 01 (500m)</text>

          {/* C2 (Right Main Conveyor - 800m) */}
          <rect x="600" y="290" width="800" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
          <text x="1000" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="3">BC MAIN - 02 (800m)</text>

          {/* Top Nodes */}
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

          {/* Bottom Nodes */}
          {[
            { id: 1, x: 40 },
            { id: 2, x: 140 },
            { id: 3, x: 240 },
            { id: 4, x: 340 },
            { id: 5, x: 440 },
            { id: 6, x: 540 }
          ].map(node => (
            <g key={`BF${node.id}`} transform={`translate(${node.x}, 380)`}>
              <rect width="20" height="70" className="fill-bg-surface stroke-border" strokeWidth="2" rx="3" />
              <text x="10" y="94" className="fill-text-secondary" fontSize="11" fontWeight="bold" textAnchor="middle">BF-{node.id}</text>
            </g>
          ))}

          {/* SENSING FIBER ROUTES (Splitted logically) */}
          
          {/* FIBER B (TF3, TF4) */}
          <path d="M 350,240 L 350,270 L 450,270 L 450,240" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          <path d="M 450,270 L 520,270 L 520,314" fill="none" strokeWidth="3" className={getStrokeClass("A-3")} />
          
          {/* FIBER A (TF1, TF2) */}
          <path d="M 150,240 L 150,260 L 250,260 L 250,240" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          <path d="M 250,260 L 520,260 L 520,270" fill="none" strokeWidth="3" className={getStrokeClass("A-2")} />
          
          {/* FIBER C (Full Length Top) */}
          <path d="M 50,290 L 540,290" fill="none" strokeWidth="3" className={getStrokeClass("A-1")} />
          
          {/* FIBER D (Bottom Tunnels BF1-BF6) */}
          <path d="M 50,380 L 50,340 L 150,340 L 150,380" fill="none" strokeWidth="3" className={getStrokeClass("A-4")} />
          <path d="M 150,340 L 250,340 L 250,380" fill="none" strokeWidth="3" className={getStrokeClass("A-5")} />
          <path d="M 250,340 L 350,340 L 350,380" fill="none" strokeWidth="3" className={getStrokeClass("A-6")} />
          <path d="M 350,340 L 450,340 L 450,380" fill="none" strokeWidth="3" className={getStrokeClass("A-7")} />
          <path d="M 450,340 L 550,340 L 550,380" fill="none" strokeWidth="3" className={getStrokeClass("A-8")} />
          <path d="M 550,340 L 580,340 L 580,314" fill="none" strokeWidth="3" className={getStrokeClass("A-9")} />

          {/* MAIN TRUNK ROUTE (C & D join to BC MAIN 02) */}
          <path d="M 520,314 L 520,324 L 580,324 L 580,314" fill="none" strokeWidth="4" stroke="#6b7280" strokeDasharray="5,5" />
          <path d="M 580,314 L 600,314 L 1400,314" fill="none" strokeWidth="3" className={getStrokeClass("A-10")} />

          {/* SYSTEM CONTROL ROOM */}
          <rect x="1350" y="270" width="80" height="80" className="fill-bg-panel stroke-border" strokeWidth="2" rx="4" />
          <circle cx="1390" cy="310" r="16" className="fill-bg-surface stroke-scada-primary" strokeWidth="2" />
          <text x="1390" y="370" className="fill-text-primary" fontSize="12" fontWeight="bold" textAnchor="middle">CONTROL ROOM</text>
        </svg>
      </div>
    </div>
  );
}
