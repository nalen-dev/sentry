import re

with open('src/features/map/MapVisualization.tsx', 'r') as f:
    content = f.read()

# Replace the whole MapVisualization.tsx content entirely to implement the requested logic cleanly.

new_content = """import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Polyline, Tooltip, useMap, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { WifiOff, Maximize, TrendingUp, LocateFixed } from 'lucide-react';
import { BC_MAIN_COORDINATES, BC_MAIN_02_COORDINATES } from '../../data/constants';

export interface LiveSegment {
  dts_ch: number;
  dts_code: number;
  main_group: string;
  start_m: number;
  end_m: number;
  temp_avg: number;
  temp_min: number;
  temp_max: number;
  temp_min_p: number;
  temp_max_p: number;
}

interface MapVisualizationProps {
  isFullscreen: boolean;
  mapZoom: number;
  setMapZoom: (zoom: number) => void;
  segments?: LiveSegment[];
  warningThreshold?: number;
  criticalThreshold?: number;
}

function MapController({ isFullscreen }: { isFullscreen: boolean }) {
  const map = useMap();

  useEffect(() => {
    const conveyorBounds: L.LatLngBoundsExpression = [
      [-0.308000, 115.857000],
      [-0.299000, 115.869000]
    ];

    if (isFullscreen) {
      map.dragging.enable();
      map.scrollWheelZoom.enable();
      map.doubleClickZoom.enable();
      map.touchZoom.enable();
      map.keyboard.enable();
    } else {
      map.dragging.disable();
      map.scrollWheelZoom.disable();
      map.doubleClickZoom.disable();
      map.touchZoom.disable();
      map.keyboard.disable();
      map.fitBounds(conveyorBounds, { 
        paddingTopLeft: [420, 10],
        paddingBottomRight: [10, 10]
      });
    }
  }, [isFullscreen, map]);

  return null;
}

// Helper to offset coordinates
const offsetCoords = (coords: [number, number][], latOffset: number, lngOffset: number): [number, number][] => {
  return coords.map(p => [p[0] + latOffset, p[1] + lngOffset]);
};

// Group Mapping and Definition
const GROUPS_MAPPING = [
  { id: 'BC4 A', color: '#06b6d4', getCoords: () => offsetCoords(BC_MAIN_COORDINATES, -0.000008, +0.000008), anchorIdx: 3 },
  { id: 'TCM16', color: '#10b981', getCoords: () => offsetCoords(BC_MAIN_COORDINATES, -0.000025, +0.000025), anchorIdx: 5 },
  { id: 'BEK34', color: '#a855f7', getCoords: () => offsetCoords(BC_MAIN_COORDINATES, +0.000008, -0.000008), anchorIdx: 7 },
  { id: 'BEK56', color: '#f97316', getCoords: () => offsetCoords(BC_MAIN_COORDINATES, +0.000025, -0.000025), anchorIdx: 9 },
  { id: 'BC4 B', color: '#ec4899', getCoords: () => BC_MAIN_02_COORDINATES.slice(0, 4), anchorIdx: 1 },
  { id: 'BC5', color: '#3b82f6', getCoords: () => BC_MAIN_02_COORDINATES.slice(4, 6), anchorIdx: 0 }, // relative to slice
  { id: 'BC45-MOTOR', color: '#8b5cf6', getCoords: () => offsetCoords(BC_MAIN_02_COORDINATES.slice(3, 5), +0.000030, +0.000000), anchorIdx: 0 },
];

export default function MapVisualization({ isFullscreen, mapZoom, setMapZoom, segments = [], warningThreshold = 45, criticalThreshold = 60 }: MapVisualizationProps) {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Process live data for each group
  const groupStatus = GROUPS_MAPPING.map(grp => {
    const grpSegments = segments.filter(s => s.main_group === grp.id);
    let maxTemp = 0;
    let criticalSegment: LiveSegment | null = null;

    grpSegments.forEach(s => {
      if (s.temp_max > maxTemp) {
        maxTemp = s.temp_max;
        criticalSegment = s;
      }
    });

    let status = 'Normal';
    let displayColor = grp.color;
    let isBlinking = false;

    if (maxTemp >= criticalThreshold) {
      status = 'Danger';
      displayColor = '#ef4444'; // Red
      isBlinking = true;
    } else if (maxTemp >= warningThreshold) {
      status = 'Warning';
      displayColor = '#eab308'; // Yellow
      isBlinking = true;
    }

    return {
      ...grp,
      maxTemp,
      status,
      displayColor,
      isBlinking,
      criticalSegment
    };
  });

  return (
    <div className="w-full h-full relative z-0">
      {!isOnline && (
        <div className="absolute inset-0 z-[1000] bg-bg-base/80 backdrop-blur-sm flex flex-col items-center justify-center text-text-primary">
          <WifiOff size={48} className="text-scada-error mb-4 opacity-80 animate-pulse" />
          <h2 className="text-xl font-bold tracking-widest text-scada-error mb-2">SATELLITE MAP UNAVAILABLE</h2>
          <p className="text-sm text-text-secondary font-mono bg-bg-panel/50 px-4 py-2 rounded-lg border border-border">
            Please connect to the internet to view the satellite background.
          </p>
        </div>
      )}

      <MapContainer 
        center={[-0.306000, 115.860000]} 
        zoom={17} 
        className={`w-full h-full ${!isFullscreen ? 'pointer-events-none' : ''}`}
        zoomControl={false}
        attributionControl={false}
      >
        <MapController isFullscreen={isFullscreen} />
        
        <TileLayer
          url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
          attribution="&copy; Google Maps"
          maxNativeZoom={18}
          maxZoom={21}
          eventHandlers={{
            tileerror: () => setIsOnline(false),
            tileload: () => { if (!isOnline) setIsOnline(true); }
          }}
        />

        {/* DRAW GROUPS */}
        {groupStatus.map((g, idx) => {
          const coords = g.getCoords();
          const anchorPoint = coords[g.anchorIdx] || coords[0];

          return (
            <React.Fragment key={g.id}>
              {/* The Polyline */}
              <Polyline 
                positions={coords} 
                pathOptions={{ 
                  color: g.displayColor, 
                  weight: (mapZoom >= 18 || isFullscreen) ? 5 : (g.id.includes('BC4 A') ? 8 : 4),
                  className: g.isBlinking ? (g.status === 'Danger' ? 'animate-pulse' : 'animate-pulse opacity-80') : ''
                }}
              />

              {/* The Tooltip/Card */}
              {anchorPoint && (
                <CircleMarker center={anchorPoint} radius={0} stroke={false} fillOpacity={0}>
                  <Tooltip 
                    direction="top" 
                    offset={[0, -10]} 
                    opacity={1} 
                    permanent 
                    className={`custom-group-card ${g.isBlinking ? (g.status === 'Danger' ? 'border-red-500 animate-pulse' : 'border-yellow-500 animate-pulse') : 'border-border'}`}
                  >
                    <div className="flex flex-col bg-bg-panel rounded-lg shadow-lg overflow-hidden border border-border min-w-[150px]">
                      {/* Header */}
                      <div className="flex items-center justify-between px-3 py-1.5" style={{ backgroundColor: `${g.displayColor}20`, borderBottom: `2px solid ${g.displayColor}` }}>
                        <span className="font-bold text-xs tracking-widest text-text-primary uppercase">{g.id}</span>
                        <span className="text-[10px] uppercase font-bold" style={{ color: g.displayColor }}>{g.status}</span>
                      </div>
                      
                      {/* Data Body */}
                      <div className="p-2 flex flex-col space-y-1 bg-bg-surface">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-text-secondary flex items-center"><TrendingUp size={10} className="mr-1"/> Max Temp</span>
                          <span className="font-mono font-bold" style={{ color: g.displayColor }}>{g.maxTemp.toFixed(1)}°C</span>
                        </div>
                        
                        {g.criticalSegment && (
                          <div className="flex items-center justify-between text-xs mt-1 pt-1 border-t border-border/50">
                            <span className="text-text-secondary flex items-center"><LocateFixed size={10} className="mr-1"/> Hotspot</span>
                            <span className="font-mono text-text-primary text-[10px] bg-bg-base px-1 rounded">{g.criticalSegment.start_m}m - {g.criticalSegment.end_m}m</span>
                          </div>
                        )}
                        {!g.criticalSegment && (
                          <div className="flex items-center justify-between text-xs mt-1 pt-1 border-t border-border/50">
                            <span className="text-text-secondary flex items-center"><LocateFixed size={10} className="mr-1"/> Hotspot</span>
                            <span className="font-mono text-text-secondary text-[10px]">No Data</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </Tooltip>
                </CircleMarker>
              )}
            </React.Fragment>
          );
        })}
      </MapContainer>
    </div>
  );
}
"""

with open('src/features/map/MapVisualization.tsx', 'w') as f:
    f.write(new_content)

