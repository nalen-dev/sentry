import { useState, useEffect } from 'react';
import { Layout } from 'lucide-react';
import { invoke } from '@tauri-apps/api/core';

interface MapCalibration {
  main_group: string;
  sub_group?: string;
  start_m: number;
  end_m: number;
  start_svg_x: number;
  start_svg_y: number;
  end_svg_x: number;
  end_svg_y: number;
}

interface LiveSegment {
  main_group: string;
  sub_group?: string | null;
  start_m?: number | null;
  end_m?: number | null;
  temp_max: number;
  temp_avg: number;
}

interface Props {
  isFullscreen: boolean;
  segments: LiveSegment[];
  warningThreshold: number;
  criticalThreshold: number;
  hideHeader?: boolean;
  alwaysShowPin?: boolean;
}


export default function DiagramVisualization({ isFullscreen, segments, warningThreshold, criticalThreshold, hideHeader, alwaysShowPin }: Props) {
  
  const [calibrations, setCalibrations] = useState<MapCalibration[]>([]);

  useEffect(() => {
    invoke<MapCalibration[]>('get_map_calibration')
      .then(setCalibrations)
      .catch(console.error);
  }, []);

  const getStatusColor = (segment: LiveSegment) => {
    if (segment.temp_avg <= -300) return 'stroke-red-500'; // Fiber Break
    if (segment.temp_max >= criticalThreshold) return 'stroke-red-500';
    if (segment.temp_max >= warningThreshold) return 'stroke-yellow-500';
    return 'stroke-green-500'; // Green
  };

  const getFillColor = (segment: LiveSegment) => {
    if (segment.temp_avg <= -300) return 'fill-red-500';
    if (segment.temp_max >= criticalThreshold) return 'fill-red-500';
    if (segment.temp_max >= warningThreshold) return 'fill-yellow-500';
    return 'fill-scada-primary';
  };

  
  // Hardcoded polylines for exact physical loops. 
  // Arrays are reversed so that index 0 is always the side CLOSER to the Control Room (0 meters).
  const SUBGROUP_PATHS: Record<string, number[][]> = {
    // TCM16 Groups (Right to Left: 0m is at Control Room, so fiber travels CR -> TCM6 -> TCM5 ...)
    'TN12': [[130, 314], [60, 314], [60, 372], [60, 314]],
    'TN23': [[200, 314], [130, 314], [130, 372], [130, 314]],
    'TN34': [[270, 314], [200, 314], [200, 372], [200, 314]],
    'TN45': [[340, 314], [270, 314], [270, 372], [270, 314]],
    'TN56': [[410, 314], [340, 314], [340, 372], [340, 314]],
    'TN6CR': [[513, 314], [410, 314], [410, 372], [410, 314]],
    'TCM6CR': [[513, 314], [410, 314], [410, 372], [410, 314]],

    // BEK34 Groups (Right to Left: CR -> BEK4 -> BEK3)
    'BEK4CR': [[513, 282], [305, 282]], 
    'BE34M': [[305, 282], [305, 220], [305, 282], [235, 282], [235, 220]],

    // BEK56 Groups (Right to Left: CR -> BEK6 -> BEK5)
    'BEK6CR': [[513, 274], [445, 274]], 
    'BEK56M': [[445, 274], [445, 220], [445, 274], [375, 274], [375, 220]]
  };

  const getPathSegments = (points: number[][]) => {
    const segs = [];
    let totalLen = 0;
    for (let i = 0; i < points.length - 1; i++) {
      const p1 = points[i];
      const p2 = points[i + 1];
      const dist = Math.sqrt(Math.pow(p2[0] - p1[0], 2) + Math.pow(p2[1] - p1[1], 2));
      segs.push({ p1, p2, len: dist, startL: totalLen });
      totalLen += dist;
    }
    return { segs, totalLen };
  };

  const interpolatePoly = (points: number[][], r1: number, r2: number) => {
    const { segs, totalLen } = getPathSegments(points);
    const targetStart = r1 * totalLen;
    const targetEnd = r2 * totalLen;
    
    const lines = [];
    
    for (const s of segs) {
      const sEndL = s.startL + s.len;
      if (sEndL > targetStart && s.startL < targetEnd) {
        const localStart = Math.max(targetStart, s.startL) - s.startL;
        const localEnd = Math.min(targetEnd, sEndL) - s.startL;
        
        const lr1 = localStart / s.len;
        const lr2 = localEnd / s.len;
        
        const x1 = s.p1[0] + lr1 * (s.p2[0] - s.p1[0]);
        const y1 = s.p1[1] + lr1 * (s.p2[1] - s.p1[1]);
        const x2 = s.p1[0] + lr2 * (s.p2[0] - s.p1[0]);
        const y2 = s.p1[1] + lr2 * (s.p2[1] - s.p1[1]);
        
        lines.push({ x1, y1, x2, y2 });
      }
    }
    return lines;
  };
const renderDynamicSegments = () => {
    return calibrations.map((calib, cIdx) => {
      const groupSegments = segments.filter(s => s.main_group === calib.main_group || (s.sub_group && s.sub_group === calib.main_group));
      
      return groupSegments.map((seg, sIdx) => {
        let startM = seg.start_m || 0;
        let endM = seg.end_m || 0;
        
        const totalM = calib.end_m - calib.start_m;
        if (totalM === 0) return null;
        
        // Fallback: If segment has no distance mapping, assume it covers the whole group
        if (startM === endM) {
            startM = calib.start_m;
            endM = calib.end_m;
        }

        let r1 = (startM - calib.start_m) / totalM;
        let r2 = (endM - calib.start_m) / totalM;
        r1 = Math.max(0, Math.min(1, r1));
        r2 = Math.max(0, Math.min(1, r2));
        if (r1 === r2) return null;

        const strokeColor = getStatusColor(seg);
        const fillColor = getFillColor(seg);
        const isAlarm = strokeColor.includes('red-500') || strokeColor.includes('yellow-500');
        const showPin = isAlarm || alwaysShowPin;

        // IF this group is one of our special polyline paths, use it!
        const polyPoints = SUBGROUP_PATHS[seg.sub_group || ''];
        
        if (polyPoints) {
          const lines = interpolatePoly(polyPoints, r1, r2);
          if (lines.length === 0) return null;
          
          // Use the midpoint of the first line segment for the alarm pin
          const midX = (lines[0].x1 + lines[0].x2) / 2;
          const midY = (lines[0].y1 + lines[0].y2) / 2;

          return (
            <g key={`${cIdx}-${sIdx}`}>
              {lines.map((l, lIdx) => (
                <line key={lIdx} x1={l.x1} y1={l.y1} x2={l.x2} y2={l.y2} strokeWidth="3" className={`${strokeColor} ${isAlarm ? 'animate-pulse' : ''} ${strokeColor.includes('red') ? 'drop-shadow-[0_0_8px_rgba(239,68,68,0.8)]' : strokeColor.includes('yellow') ? 'drop-shadow-[0_0_8px_rgba(234,179,8,0.8)]' : ''} transition-colors duration-500`} strokeLinecap="round" />
              ))}
              {showPin && (
                <g transform={`translate(${midX}, ${midY})`} className={isAlarm ? "animate-bounce animate-pulse" : ""}>
                  <path d="M0 -15 C 8 -15 12 -7 12 0 C 12 8 0 15 0 15 C 0 15 -12 8 -12 0 C -12 -7 -8 -15 0 -15" className={fillColor} />
                  <circle cx="0" cy="-5" r="4" fill="white" />
                </g>
              )}
            </g>
          );
        } else {
          // Prevent drawing the old buggy fallback straight lines for groups that are now handled strictly by subgroup polylines
          if (['TCM16', 'BEK56', 'BEK34'].includes(calib.main_group)) return null;

          // Standard straight line interpolation for non-poly paths (e.g. BC4 A, BC4 B)
          const x1 = calib.start_svg_x + r1 * (calib.end_svg_x - calib.start_svg_x);
          const y1 = calib.start_svg_y + r1 * (calib.end_svg_y - calib.start_svg_y);
          const x2 = calib.start_svg_x + r2 * (calib.end_svg_x - calib.start_svg_x);
          const y2 = calib.start_svg_y + r2 * (calib.end_svg_y - calib.start_svg_y);
          const midX = (x1 + x2) / 2;
          const midY = (y1 + y2) / 2;
          return (
            <g key={`${cIdx}-${sIdx}`}>
              <line x1={x1} y1={y1} x2={x2} y2={y2} strokeWidth="3" className={`${strokeColor} ${isAlarm ? 'animate-pulse' : ''} ${strokeColor.includes('red') ? 'drop-shadow-[0_0_8px_rgba(239,68,68,0.8)]' : strokeColor.includes('yellow') ? 'drop-shadow-[0_0_8px_rgba(234,179,8,0.8)]' : ''} transition-colors duration-500`} strokeLinecap="round" />
              {showPin && (
                <g transform={`translate(${midX}, ${midY})`} className={isAlarm ? "animate-bounce animate-pulse" : ""}>
                  <path d="M0 -15 C 8 -15 12 -7 12 0 C 12 8 0 15 0 15 C 0 15 -12 8 -12 0 C -12 -7 -8 -15 0 -15" className={fillColor} />
                  <circle cx="0" cy="-5" r="4" fill="white" />
                </g>
              )}
            </g>
          );
        }
      });
    });
  };


  
  let customViewBox = "0 0 1450 600";
  let customClass = "w-[1600px] h-[660px] min-w-[1200px] drop-shadow-2xl -translate-y-8";
  
  if (alwaysShowPin && segments.length === 1 && calibrations.length > 0) {
     const seg = segments[0];
     // Find calibration
     const calib = calibrations.find(c => c.main_group === seg.main_group || c.main_group === seg.sub_group);
     if (calib) {
         let midX = (calib.start_svg_x + calib.end_svg_x) / 2;
         let midY = (calib.start_svg_y + calib.end_svg_y) / 2;
         
         const polyPoints = SUBGROUP_PATHS[seg.sub_group || ''];
         if (polyPoints) {
            midX = (polyPoints[0][0] + polyPoints[polyPoints.length - 1][0]) / 2;
            midY = (polyPoints[0][1] + polyPoints[polyPoints.length - 1][1]) / 2;
         }
         
         // Zoom into 600x400 around midX, midY
         const vw = 500;
         const vh = 300;
         const vx = Math.max(0, midX - vw / 2);
         const vy = Math.max(0, midY - vh / 2);
         customViewBox = `${vx} ${vy} ${vw} ${vh}`;
         customClass = "w-full h-full drop-shadow-2xl"; // make it fill modal without scroll
     }
  }

return (
    <div className="w-full h-full bg-bg-panel flex flex-col relative overflow-hidden custom-scrollbar p-6">
      
      {/* HEADER P&ID */}
      {!hideHeader && <div className={`flex justify-between items-center mb-4 shrink-0 bg-bg-surface p-4 rounded-xl border border-border shadow-lg z-10 ${!isFullscreen ? 'ml-[400px]' : ''} transition-all duration-500`}>
        <div className="flex items-center">
          <Layout className="text-scada-primary mr-3" size={24} />
          <div>
            <h2 className="text-text-primary font-bold tracking-widest text-lg">DTS SCHEMATIC VIEW</h2>
            <p className="text-text-secondary text-xs font-mono">DISTRIBUTED TEMPERATURE SENSING</p>
          </div>
        </div>
      </div>}

      {/* SVG CANVAS */}
      <div className={`flex-1 bg-bg-base border border-border rounded-xl overflow-auto custom-scrollbar relative shadow-scada-inset flex items-center justify-center ${(!isFullscreen && !hideHeader) ? 'pl-[400px]' : ''} transition-all duration-500`}>
                <svg viewBox={customViewBox} className={customClass}>
          
          <defs>
            <pattern id="dotGrid" width="30" height="30" patternUnits="userSpaceOnUse">
              <circle cx="2" cy="2" r="1" className="fill-border" />
            </pattern>
          </defs>
          
          <rect width="100%" height="100%" fill="url(#dotGrid)" />

          {/* BC4 A (Left Conveyor, proportional 591m = ~473px) */}
          <rect x="40" y="290" width="473" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
          <text x="276" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="3">BC4 A</text>

          {/* BC4 B (Right Conveyor, proportional 877m = ~702px) */}
          <rect x="523" y="290" width="702" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
          <text x="874" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="2">BC4 B</text>
          
          {/* BC5 (Right End Conveyor, proportional 150m = ~120px) */}
          <rect x="1235" y="290" width="120" height="24" className="fill-bg-surface stroke-border" strokeWidth="2" rx="4" />
          <text x="1295" y="306" className="fill-text-secondary" fontSize="12" fontWeight="bold" textAnchor="middle" letterSpacing="2">BC5</text>

          {/* Top Nodes (TN BEK 3 - 6, before Control Room) */}
          {[
            { id: 'TN BEK 3', x: 215 },
            { id: 'TN BEK 4', x: 285 },
            { id: 'TN BEK 5', x: 355 },
            { id: 'TN BEK 6', x: 425 }
          ].map((node, i) => (
            <g key={`TF${i}`} transform={`translate(${node.x}, 220)`}>
              <rect width="20" height="50" className="fill-bg-surface stroke-border" strokeWidth="2" rx="3" />
              <text x="10" y="-12" className="fill-text-secondary" fontSize="11" fontWeight="bold" textAnchor="middle">{node.id}</text>
            </g>
          ))}

          {/* Bottom Nodes (TN TCM 1 - 6, left side) */}
          {[
            { id: 'TN TCM 1', x: 40 },
            { id: 'TN TCM 2', x: 110 },
            { id: 'TN TCM 3', x: 180 },
            { id: 'TN TCM 4', x: 250 },
            { id: 'TN TCM 5', x: 320 },
            { id: 'TN TCM 6', x: 390 }
          ].map((node, i) => (
            <g key={`BF${i}`} transform={`translate(${node.x}, 332)`}>
              <rect width="20" height="40" className="fill-bg-surface stroke-border" strokeWidth="2" rx="3" />
              <text x="10" y="64" className="fill-text-secondary" fontSize="11" fontWeight="bold" textAnchor="middle">{node.id}</text>
            </g>
          ))}

          {/* SENSING FIBER ROUTES */}
          {/* Single Vertical Trunk bundle entering Control Room */}
          <path d="M 513,274 L 513,360" fill="none" strokeWidth="3" className="stroke-scada-primary" strokeDasharray="5,5" />
          
          {/* Fiber BC4 A (goes left to x=40 on TOP of conveyor y=290) */}
          <path d="M 513,290 L 40,290" fill="none" strokeWidth="3" className="stroke-border/40" />
          
          {/* Fiber BC4 B (starts at control room x=513, goes right to x=1225 on BOTTOM of conveyor y=314) */}
          <path d="M 513,314 L 1225,314" fill="none" strokeWidth="3" className="stroke-border/40" />
          
          {/* Fiber BC5 (starts from end of BC4 B x=1225, goes to x=1355 on BOTTOM of conveyor y=314) */}
          <path d="M 1225,314 L 1235,314" fill="none" strokeWidth="2" className="stroke-border" strokeDasharray="2,2" />
          <path d="M 1235,314 L 1355,314" fill="none" strokeWidth="3" className="stroke-border/40" />          
          {/* 40m Cable at Top between BC4 B and BC5 */}
          <path d="M 1209,290 L 1241,290" fill="none" strokeWidth="3" className="stroke-border/40" />
          
          {/* FIBER B (TN BEK 3, TN BEK 4) */}
          <path d="M 235,220 L 235,282" fill="none" strokeWidth="3" className="stroke-border/40" />
          <path d="M 305,220 L 305,282" fill="none" strokeWidth="3" className="stroke-border/40" />
          <path d="M 235,282 L 513,282" fill="none" strokeWidth="3" className="stroke-border/40" />
          
          {/* FIBER A (TN BEK 5, TN BEK 6) */}
          <path d="M 375,220 L 375,274" fill="none" strokeWidth="3" className="stroke-border/40" />
          <path d="M 445,220 L 445,274" fill="none" strokeWidth="3" className="stroke-border/40" />
          <path d="M 375,274 L 513,274" fill="none" strokeWidth="3" className="stroke-border/40" />
          
          {/* FIBER D (Bottom Tunnels TN TCM 1-6, Left Side) */}
          <path d="M 60,372 L 60,314" fill="none" strokeWidth="3" className="stroke-border/40" />
          <path d="M 130,372 L 130,314" fill="none" strokeWidth="3" className="stroke-border/40" />
          <path d="M 200,372 L 200,314" fill="none" strokeWidth="3" className="stroke-border/40" />
          <path d="M 270,372 L 270,314" fill="none" strokeWidth="3" className="stroke-border/40" />
          <path d="M 340,372 L 340,314" fill="none" strokeWidth="3" className="stroke-border/40" />
          <path d="M 410,372 L 410,314" fill="none" strokeWidth="3" className="stroke-border/40" />
          <path d="M 60,314 L 410,314" fill="none" strokeWidth="3" className="stroke-border/40" />
          <path d="M 410,314 L 513,314" fill="none" strokeWidth="3" className="stroke-border/40" />

          {renderDynamicSegments()}

          {/* SYSTEM CONTROL ROOM */}
          <g transform="translate(473, 360)">
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
