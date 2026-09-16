import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# Add imports
imports = """import { useState, useEffect } from 'react';
import { Layout } from 'lucide-react';
import { invoke } from '@tauri-apps/api/core';

interface MapCalibration {
  main_group: string;
  start_m: number;
  end_m: number;
  start_svg_x: number;
  start_svg_y: number;
  end_svg_x: number;
  end_svg_y: number;
}

interface LiveSegment {
  main_group: string;
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
}
"""
code = code.replace("import { Layout } from 'lucide-react';\nimport { DUMMY_AREAS } from '../../data/constants';", imports)

# Update component signature
code = code.replace("export default function DiagramVisualization({ isFullscreen }: { isFullscreen: boolean }) {", "export default function DiagramVisualization({ isFullscreen, segments, warningThreshold, criticalThreshold }: Props) {")

# Add state and logic for calibrations
logic = """
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
    return 'stroke-scada-primary'; // Green
  };

  const getFillColor = (segment: LiveSegment) => {
    if (segment.temp_avg <= -300) return 'fill-red-500';
    if (segment.temp_max >= criticalThreshold) return 'fill-red-500';
    if (segment.temp_max >= warningThreshold) return 'fill-yellow-500';
    return 'fill-scada-primary';
  };

  const renderDynamicSegments = () => {
    return calibrations.map((calib, cIdx) => {
      // Find all segments assigned to this group
      const groupSegments = segments.filter(s => s.main_group === calib.main_group);
      
      return groupSegments.map((seg, sIdx) => {
        const startM = seg.start_m || 0;
        const endM = seg.end_m || 0;
        if (startM === endM) return null;

        // Calculate ratios
        const totalM = calib.end_m - calib.start_m;
        if (totalM === 0) return null;

        let r1 = (startM - calib.start_m) / totalM;
        let r2 = (endM - calib.start_m) / totalM;

        // Clamp between 0 and 1
        r1 = Math.max(0, Math.min(1, r1));
        r2 = Math.max(0, Math.min(1, r2));

        if (r1 === r2) return null; // Outside calibration bounds

        const x1 = calib.start_svg_x + r1 * (calib.end_svg_x - calib.start_svg_x);
        const y1 = calib.start_svg_y + r1 * (calib.end_svg_y - calib.start_svg_y);
        const x2 = calib.start_svg_x + r2 * (calib.end_svg_x - calib.start_svg_x);
        const y2 = calib.start_svg_y + r2 * (calib.end_svg_y - calib.start_svg_y);

        const strokeColor = getStatusColor(seg);
        const fillColor = getFillColor(seg);
        const isAlarm = strokeColor.includes('red-500') || strokeColor.includes('yellow-500');

        const midX = (x1 + x2) / 2;
        const midY = (y1 + y2) / 2;

        return (
          <g key={`${cIdx}-${sIdx}`}>
            <line x1={x1} y1={y1} x2={x2} y2={y2} strokeWidth="5" className={`${strokeColor} ${strokeColor.includes('red') ? 'animate-pulse drop-shadow-[0_0_8px_rgba(239,68,68,0.8)]' : ''} transition-colors duration-500`} strokeLinecap="round" />
            
            {/* Draw Pin for Alarms */}
            {isAlarm && (
              <g transform={`translate(${midX}, ${midY})`}>
                <circle cx="0" cy="0" r="12" className={`${fillColor} animate-ping opacity-75`} />
                <circle cx="0" cy="0" r="6" className={`${fillColor} drop-shadow-[0_0_10px_rgba(0,0,0,0.5)]`} />
              </g>
            )}
          </g>
        );
      });
    });
  };
"""

# Replace `getStrokeClass` and its usages
# Since base paths should be gray, we'll replace `className={getStrokeClass("...")}` with `className="stroke-border/50"`
code = re.sub(r'const getStrokeClass = \([^)]+\) => \{[^}]+\};', logic, code, flags=re.DOTALL)
code = re.sub(r'className=\{getStrokeClass\("[^"]+"\)\}', 'className="stroke-border/40"', code)

# Insert the dynamic segments just before the control room
code = code.replace("{/* SYSTEM CONTROL ROOM */}", "{renderDynamicSegments()}\n\n          {/* SYSTEM CONTROL ROOM */}")

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

