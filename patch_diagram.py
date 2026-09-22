import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    content = f.read()

# Add focus state
state_old = "const [calibrations, setCalibrations] = useState<MapCalibration[]>([]);"
state_new = "const [calibrations, setCalibrations] = useState<MapCalibration[]>([]);\n  const [focusPoint, setFocusPoint] = useState<{x: number, y: number} | null>(null);"
content = content.replace(state_old, state_new)

# Modify renderDynamicSegments to capture focus point
# Wait, renderDynamicSegments is called during render. We shouldn't setState during render.
# Better to use a useMemo to compute focusPoint based on segments and calibrations, OR just let the SVG viewBox be calculated inline.

render_func_start = "const renderDynamicSegments = () => {"
render_func_end = "return calibrations.map((calib, cIdx) => {"

# We can just change the viewBox inline.
viewbox_old = '<svg viewBox="0 0 1450 600" className="w-[1600px] h-[660px] min-w-[1200px] drop-shadow-2xl -translate-y-8">'

viewbox_logic = """
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

"""

content = content.replace(
    'return (\n    <div className="w-full',
    viewbox_logic + 'return (\n    <div className="w-full'
)

content = content.replace(viewbox_old, '<svg viewBox={customViewBox} className={customClass}>')

with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(content)

