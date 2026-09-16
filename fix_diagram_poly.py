import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    code = f.read()

# 1. Update stroke color and width
code = code.replace("return 'stroke-scada-primary';", "return 'stroke-green-500';")
code = code.replace("strokeWidth=\"5\"", "strokeWidth=\"3\"")

# 2. Add Polyline interpolation logic
poly_logic = """
  // Hardcoded polylines for exact physical loops
  const SUBGROUP_PATHS: Record<string, number[][]> = {
    // TCM16 Loops (Starts from bottom of tunnel)
    'TN12': [[60, 372], [60, 314], [130, 314], [130, 372]],
    'TN23': [[130, 372], [130, 314], [200, 314], [200, 372]],
    'TN34': [[200, 372], [200, 314], [270, 314], [270, 372]],
    'TN45': [[270, 372], [270, 314], [340, 314], [340, 372]], // Added TN45 just in case
    'TN56': [[340, 372], [340, 314], [410, 314], [410, 372]],
    'TN6CR': [[410, 372], [410, 314], [513, 314], [513, 360]], // Connected down to Control Room

    // BEK34 Loops
    'BE34M': [[235, 220], [235, 282], [305, 282], [305, 220]],
    'BEK4CR': [[305, 220], [305, 282], [513, 282], [513, 360]],

    // BEK56 Loops
    'BEK56M': [[375, 220], [375, 274], [445, 274], [445, 220]],
    'BEK6CR': [[445, 220], [445, 274], [513, 274], [513, 360]]
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
"""

# Now replace the renderDynamicSegments function body
old_render = """const renderDynamicSegments = () => {
    return calibrations.map((calib, cIdx) => {
      // Find all segments assigned to this group
      const groupSegments = segments.filter(s => s.main_group === calib.main_group || (s.sub_group && s.sub_group === calib.main_group));
      
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
            <line x1={x1} y1={y1} x2={x2} y2={y2} strokeWidth="3" className={`${strokeColor} ${strokeColor.includes('red') ? 'animate-pulse drop-shadow-[0_0_8px_rgba(239,68,68,0.8)]' : ''} transition-colors duration-500`} strokeLinecap="round" />
            
            {/* Draw Pin for Alarms */}
            {isAlarm && (
              <g transform={`translate(${midX}, ${midY})`} className="animate-bounce">
                <path d="M0 -15 C 8 -15 12 -7 12 0 C 12 8 0 15 0 15 C 0 15 -12 8 -12 0 C -12 -7 -8 -15 0 -15" className={fillColor} />
                <circle cx="0" cy="-5" r="4" fill="white" />
              </g>
            )}
          </g>
        );
      });
    });
  };"""

# Wait, strokeWidth="5" was there in my previous code, I just ran a replace for 3, so let's match with a regex.
import re

old_render_regex = r"const renderDynamicSegments = \(\) => \{[\s\S]*?\}\);\s*\}\);\s*\};"

new_render = """const renderDynamicSegments = () => {
    return calibrations.map((calib, cIdx) => {
      const groupSegments = segments.filter(s => s.main_group === calib.main_group || (s.sub_group && s.sub_group === calib.main_group));
      
      return groupSegments.map((seg, sIdx) => {
        const startM = seg.start_m || 0;
        const endM = seg.end_m || 0;
        if (startM === endM) return null;

        const totalM = calib.end_m - calib.start_m;
        if (totalM === 0) return null;

        let r1 = (startM - calib.start_m) / totalM;
        let r2 = (endM - calib.start_m) / totalM;
        r1 = Math.max(0, Math.min(1, r1));
        r2 = Math.max(0, Math.min(1, r2));
        if (r1 === r2) return null;

        const strokeColor = getStatusColor(seg);
        const fillColor = getFillColor(seg);
        const isAlarm = strokeColor.includes('red-500') || strokeColor.includes('yellow-500');

        // IF this group is one of our special polyline paths, use it!
        const polyPoints = SUBGROUP_PATHS[calib.main_group];
        
        if (polyPoints) {
          const lines = interpolatePoly(polyPoints, r1, r2);
          if (lines.length === 0) return null;
          
          // Use the midpoint of the first line segment for the alarm pin
          const midX = (lines[0].x1 + lines[0].x2) / 2;
          const midY = (lines[0].y1 + lines[0].y2) / 2;

          return (
            <g key={`${cIdx}-${sIdx}`}>
              {lines.map((l, lIdx) => (
                <line key={lIdx} x1={l.x1} y1={l.y1} x2={l.x2} y2={l.y2} strokeWidth="3" className={`${strokeColor} ${strokeColor.includes('red') ? 'animate-pulse drop-shadow-[0_0_8px_rgba(239,68,68,0.8)]' : ''} transition-colors duration-500`} strokeLinecap="round" />
              ))}
              {isAlarm && (
                <g transform={`translate(${midX}, ${midY})`} className="animate-bounce">
                  <path d="M0 -15 C 8 -15 12 -7 12 0 C 12 8 0 15 0 15 C 0 15 -12 8 -12 0 C -12 -7 -8 -15 0 -15" className={fillColor} />
                  <circle cx="0" cy="-5" r="4" fill="white" />
                </g>
              )}
            </g>
          );
        } else {
          // Standard straight line interpolation for non-poly paths (e.g. BC4 A, BC4 B)
          const x1 = calib.start_svg_x + r1 * (calib.end_svg_x - calib.start_svg_x);
          const y1 = calib.start_svg_y + r1 * (calib.end_svg_y - calib.start_svg_y);
          const x2 = calib.start_svg_x + r2 * (calib.end_svg_x - calib.start_svg_x);
          const y2 = calib.start_svg_y + r2 * (calib.end_svg_y - calib.start_svg_y);
          const midX = (x1 + x2) / 2;
          const midY = (y1 + y2) / 2;
          return (
            <g key={`${cIdx}-${sIdx}`}>
              <line x1={x1} y1={y1} x2={x2} y2={y2} strokeWidth="3" className={`${strokeColor} ${strokeColor.includes('red') ? 'animate-pulse drop-shadow-[0_0_8px_rgba(239,68,68,0.8)]' : ''} transition-colors duration-500`} strokeLinecap="round" />
              {isAlarm && (
                <g transform={`translate(${midX}, ${midY})`} className="animate-bounce">
                  <path d="M0 -15 C 8 -15 12 -7 12 0 C 12 8 0 15 0 15 C 0 15 -12 8 -12 0 C -12 -7 -8 -15 0 -15" className={fillColor} />
                  <circle cx="0" cy="-5" r="4" fill="white" />
                </g>
              )}
            </g>
          );
        }
      });
    });
  };"""

code = re.sub(old_render_regex, poly_logic + new_render, code)

# Fix the bug with the random line above/below control room by making sure we don't accidentally draw bad coordinates
# Actually, the bad lines were caused by old map_calibration entries. The new migration deletes them. But I'll delete the `TCM16` fallback calibration from DB in my instructions.

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(code)

