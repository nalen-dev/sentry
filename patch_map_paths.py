import re

with open('src/features/map/MapVisualization.tsx', 'r') as f:
    content = f.read()

# Replace the GROUPS_MAPPING completely to use TUNNEL_SENSORS for the 3 groups
new_mapping = """import { BC_MAIN_COORDINATES, BC_MAIN_02_COORDINATES, TUNNEL_SENSORS, GROUP_COLORS } from '../../data/constants';

// Helper to offset coordinates
const offsetCoords = (coords: [number, number][], latOffset: number, lngOffset: number): [number, number][] => {
  return coords.map(p => [p[0] + latOffset, p[1] + lngOffset]);
};

const foD_coords = TUNNEL_SENSORS.foD.map(s => s.coord);
const foB_coords = TUNNEL_SENSORS.foB.map(s => s.coord);
const foA_coords = TUNNEL_SENSORS.foA.map(s => s.coord);

const GROUPS_MAPPING = [
  { id: 'BC4 A', color: GROUP_COLORS['BC4 A'], getCoords: () => BC_MAIN_COORDINATES, anchorIdx: 4, dir: 'left', offset: [-15, 0] },
  { id: 'TCM16', color: GROUP_COLORS['TCM16'], getCoords: () => offsetCoords([...foD_coords, ...BC_MAIN_COORDINATES.slice(10)], -0.000015, +0.000015), anchorIdx: 2, dir: 'bottom', offset: [0, 15] },
  { id: 'BEK34', color: GROUP_COLORS['BEK34'], getCoords: () => offsetCoords([...foB_coords, ...BC_MAIN_COORDINATES.slice(8)], +0.000015, -0.000015), anchorIdx: 0, dir: 'right', offset: [15, 0] },
  { id: 'BEK56', color: GROUP_COLORS['BEK56'], getCoords: () => offsetCoords([...foA_coords, ...BC_MAIN_COORDINATES.slice(12)], +0.000030, -0.000030), anchorIdx: 0, dir: 'top', offset: [0, -15] },
  { id: 'BC4 B', color: GROUP_COLORS['BC4 B'], getCoords: () => BC_MAIN_02_COORDINATES.slice(0, 4), anchorIdx: 1, dir: 'bottom', offset: [0, 15] },
  { id: 'BC5', color: GROUP_COLORS['BC5'], getCoords: () => BC_MAIN_02_COORDINATES.slice(4, 6), anchorIdx: 1, dir: 'top', offset: [0, -15] },
  { id: 'BC45-MOTOR', color: GROUP_COLORS['BC45-MOTOR'], getCoords: () => offsetCoords(BC_MAIN_02_COORDINATES.slice(3, 5), +0.000030, +0.000000), anchorIdx: 0, dir: 'left', offset: [-15, 0] },
];
"""
content = re.sub(r"import \{ BC_MAIN_COORDINATES.*?\n\nconst GROUPS_MAPPING = \[.*?\];\n", new_mapping, content, flags=re.DOTALL)

# Update Blinking Logic in the render map
content = content.replace("className: g.isBlinking ? (g.status === 'Danger' ? 'animate-pulse' : 'animate-pulse opacity-80') : ''", "className: g.isBlinking ? (g.status === 'Danger' ? 'map-blink-danger-svg' : 'map-blink-warning-svg') : ''")

# Replace blinking ui classes on Tooltip
content = content.replace("className={`custom-group-card cursor-pointer ${g.isBlinking ? (g.status === 'Danger' ? 'border-red-500 animate-pulse' : 'border-yellow-500 animate-pulse') : 'border-border'}`}", "className=\"custom-group-card cursor-pointer\"")

# Apply blinking ui classes directly to the inner div
content = content.replace("className=\"flex flex-col bg-bg-panel rounded-lg shadow-lg overflow-hidden border border-border min-w-[150px] pointer-events-auto hover:scale-105 transition-transform\"", "className={`flex flex-col bg-bg-panel rounded-lg shadow-lg overflow-hidden border min-w-[150px] pointer-events-auto hover:scale-105 transition-transform ${g.isBlinking ? (g.status === 'Danger' ? 'map-blink-danger-ui border-red-500' : 'map-blink-warning-ui border-yellow-500') : 'border-border'}`}")

with open('src/features/map/MapVisualization.tsx', 'w') as f:
    f.write(content)

