// @ts-nocheck
import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Polyline, Tooltip, useMap, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { WifiOff, TrendingUp, LocateFixed } from 'lucide-react';
import { BC_MAIN_COORDINATES, BC_MAIN_02_COORDINATES, GROUP_COLORS } from '../../data/constants';
import { SegmentData } from '../../components/SegmentDetailModal';

export interface LiveSegment {
  id?: number;
  dts_ch: number;
  dts_code: number;
  main_group: string;
  start_m?: number | null;
  end_m?: number | null;
  temp_avg: number;
  temp_min: number;
  temp_max: number;
  temp_min_p?: number | null;
  temp_max_p?: number | null;
  original_name?: string;
  custom_name?: string | null;
}

interface MapVisualizationProps {
  isFullscreen: boolean;
  mapZoom: number;
  setMapZoom: (zoom: number) => void;
  segments?: LiveSegment[];
  warningThreshold?: number;
  criticalThreshold?: number;
  setSelectedSegment?: (seg: SegmentData | null) => void;
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

const offsetCoords = (coords: [number, number][], latOffset: number, lngOffset: number): [number, number][] => {
  return coords.map(p => [p[0] + latOffset, p[1] + lngOffset]);
};

// Spread out the anchors and directions so they don't overlap in default view
const GROUPS_MAPPING = [
  { id: 'BC4 A', color: GROUP_COLORS['BC4 A'], getCoords: () => offsetCoords(BC_MAIN_COORDINATES, -0.000008, +0.000008), anchorIdx: 3, dir: 'left', offset: [-15, 0] },
  { id: 'TCM16', color: GROUP_COLORS['TCM16'], getCoords: () => offsetCoords(BC_MAIN_COORDINATES, -0.000025, +0.000025), anchorIdx: 7, dir: 'bottom', offset: [0, 15] },
  { id: 'BEK34', color: GROUP_COLORS['BEK34'], getCoords: () => offsetCoords(BC_MAIN_COORDINATES, +0.000008, -0.000008), anchorIdx: 10, dir: 'right', offset: [15, 0] },
  { id: 'BEK56', color: GROUP_COLORS['BEK56'], getCoords: () => offsetCoords(BC_MAIN_COORDINATES, +0.000025, -0.000025), anchorIdx: 13, dir: 'top', offset: [0, -15] },
  { id: 'BC4 B', color: GROUP_COLORS['BC4 B'], getCoords: () => BC_MAIN_02_COORDINATES.slice(0, 4), anchorIdx: 1, dir: 'bottom', offset: [0, 15] },
  { id: 'BC5', color: GROUP_COLORS['BC5'], getCoords: () => BC_MAIN_02_COORDINATES.slice(4, 6), anchorIdx: 1, dir: 'top', offset: [0, -15] },
  { id: 'BC45-MOTOR', color: GROUP_COLORS['BC45-MOTOR'], getCoords: () => offsetCoords(BC_MAIN_02_COORDINATES.slice(3, 5), +0.000030, +0.000000), anchorIdx: 0, dir: 'left', offset: [-15, 0] },
];

export default function MapVisualization({ isFullscreen, mapZoom, setMapZoom, segments = [], warningThreshold = 45, criticalThreshold = 60, setSelectedSegment }: MapVisualizationProps) {
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

  const handleGroupClick = (criticalSegment: LiveSegment, maxTemp: number, status: string, isAlarm: boolean, groupName: string) => {
    if (setSelectedSegment && criticalSegment) {
      const segData: SegmentData = {
        id: criticalSegment.id || 0,
        name: criticalSegment.custom_name || criticalSegment.original_name || `${groupName} Hotspot`,
        status: status,
        temp: maxTemp,
        distance: `${criticalSegment.start_m}m - ${criticalSegment.end_m}m`,
        isAlarm: isAlarm,
        group: groupName,
        temp_max: criticalSegment.temp_max,
        temp_min: criticalSegment.temp_min,
        temp_avg: criticalSegment.temp_avg,
        dts_ch: criticalSegment.dts_ch,
        dts_code: criticalSegment.dts_code,
        mainGroup: groupName,
        subGroup: criticalSegment.sub_group || undefined,
        start_m: criticalSegment.start_m || undefined,
        end_m: criticalSegment.end_m || undefined,
        original_name: criticalSegment.original_name
      };
      setSelectedSegment(segData);
    }
  };

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
    let isAlarm = false;

    if (maxTemp >= criticalThreshold) {
      status = 'Danger';
      displayColor = '#ef4444'; // Red
      isBlinking = true;
      isAlarm = true;
    } else if (maxTemp >= warningThreshold) {
      status = 'Warning';
      displayColor = '#eab308'; // Yellow
      isBlinking = true;
      isAlarm = true;
    }

    return {
      ...grp,
      maxTemp,
      status,
      displayColor,
      isBlinking,
      isAlarm,
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

      {/* zoomControl is restored to default (true) by removing zoomControl={false} */}
      <MapContainer 
        center={[-0.306000, 115.860000]} 
        zoom={17} 
        className={`w-full h-full ${!isFullscreen ? 'pointer-events-none' : ''}`}
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

        {groupStatus.map((g, idx) => {
          const coords = g.getCoords();
          // Safe fallback for anchorPoint if array is smaller than expected
          const anchorPoint = coords[g.anchorIdx] || coords[coords.length - 1] || coords[0];

          return (
            <React.Fragment key={g.id}>
              <Polyline 
                positions={coords} 
                pathOptions={{ 
                  color: g.displayColor, 
                  weight: (mapZoom >= 18 || isFullscreen) ? 5 : (g.id.includes('BC4 A') ? 8 : 4),
                  className: g.isBlinking ? (g.status === 'Danger' ? 'map-blink-danger-svg' : 'map-blink-warning-svg') : ''
                }}
              />

              {anchorPoint && (
                <CircleMarker center={anchorPoint} radius={0} stroke={false} fillOpacity={0}>
                  <Tooltip 
                    direction={g.dir as any} 
                    offset={g.offset as any} 
                    opacity={1} 
                    permanent 
                    className="custom-group-card cursor-pointer"
                  >
                    <div 
                      onClick={() => {
                        if (g.criticalSegment) {
                           handleGroupClick(g.criticalSegment, g.maxTemp, g.status, g.isAlarm, g.id);
                        }
                      }}
                      className={`flex flex-col bg-bg-panel rounded-lg shadow-lg overflow-hidden border min-w-[150px] pointer-events-auto hover:scale-105 transition-transform ${g.isBlinking ? (g.status === 'Danger' ? 'map-blink-danger-ui border-red-500' : 'map-blink-warning-ui border-yellow-500') : 'border-border'}`}
                    >
                      <div className="flex items-center justify-between px-3 py-1.5" style={{ backgroundColor: `${g.displayColor}20`, borderBottom: `2px solid ${g.displayColor}` }}>
                        <span className="font-bold text-xs tracking-widest text-text-primary uppercase">{g.id}</span>
                        <span className="text-[10px] uppercase font-bold" style={{ color: g.displayColor }}>{g.status}</span>
                      </div>
                      
                      <div className="p-2 flex flex-col space-y-1 bg-bg-surface">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-text-secondary flex items-center"><TrendingUp size={10} className="mr-1"/> Max Temp</span>
                          <span className="font-mono font-bold" style={{ color: g.displayColor }}>{g.maxTemp.toFixed(1)}°C</span>
                        </div>
                        
                        {g.criticalSegment ? (
                          <div className="flex items-center justify-between text-xs mt-1 pt-1 border-t border-border/50">
                            <span className="text-text-secondary flex items-center"><LocateFixed size={10} className="mr-1"/> Hotspot</span>
                            <span className="font-mono text-text-primary text-[10px] bg-bg-base px-1 rounded">{g.criticalSegment.start_m}m - {g.criticalSegment.end_m}m</span>
                          </div>
                        ) : (
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
