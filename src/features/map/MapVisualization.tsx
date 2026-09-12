import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Polyline, Tooltip, useMap, useMapEvents, CircleMarker } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { WifiOff } from 'lucide-react';
import { BC_MAIN_COORDINATES, BC_MAIN_02_COORDINATES, TUNNEL_SENSORS } from '../../data/constants';

function MapController({ isFullscreen }: { isFullscreen: boolean }) {
  const map = useMap();

  useEffect(() => {
    // Kordinat ujung-ke-ujung conveyor (BC MAIN 01 & 02)
    const conveyorBounds: L.LatLngBoundsExpression = [
      [-0.308000, 115.857000], // SW
      [-0.299000, 115.869000]  // NE
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
        paddingTopLeft: [420, 10],      // [Kiri (kompensasi panel), Atas]
        paddingBottomRight: [10, 10]    // [Kanan, Bawah] dibuat sekecil mungkin
      });
    }

    // Pastikan Leaflet merender ulang kotak jika ada perubahan ukuran DOM
    setTimeout(() => {
      map.invalidateSize();
    }, 300);
  }, [isFullscreen, map]);

  return null;
}

function MapZoomListener({ setMapZoom }: { setMapZoom: (zoom: number) => void }) {
  const map = useMapEvents({
    zoomend: () => {
      setMapZoom(map.getZoom());
    }
  });
  return null;
}

function getClosestPointOnPath(point: [number, number], path: [number, number][]): [number, number] {
  let closestDist = Infinity;
  let closestPoint = path[0];

  for (let i = 0; i < path.length - 1; i++) {
    const A = path[i];
    const B = path[i+1];
    
    const dx = B[0] - A[0];
    const dy = B[1] - A[1];
    
    const lengthSquared = dx * dx + dy * dy;
    
    let t = 0;
    if (lengthSquared !== 0) {
      t = ((point[0] - A[0]) * dx + (point[1] - A[1]) * dy) / lengthSquared;
      t = Math.max(0, Math.min(1, t)); // clamp to segment
    }
    
    const projX = A[0] + t * dx;
    const projY = A[1] + t * dy;
    
    const distSq = (point[0] - projX) ** 2 + (point[1] - projY) ** 2;
    if (distSq < closestDist) {
      closestDist = distSq;
      closestPoint = [projX, projY];
    }
  }
  return closestPoint;
}

interface MapVisualizationProps {
  isFullscreen: boolean;
  mapZoom: number;
  setMapZoom: (zoom: number) => void;
}

export default function MapVisualization({ isFullscreen, mapZoom, setMapZoom }: MapVisualizationProps) {
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
        bounds={[
          [-0.308000, 115.857000],
          [-0.299000, 115.869000]
        ]}
        minZoom={15}
        maxZoom={21}
        maxBounds={[
          [-0.315000, 115.850000],
          [-0.290000, 115.880000]
        ]}
        maxBoundsViscosity={1.0}
        className="w-full h-full"
        zoomControl={false}
      >
        <MapController isFullscreen={isFullscreen} />
        <MapZoomListener setMapZoom={setMapZoom} />
        
        {/* GOOGLE SATELLITE TILE SERVER */}
        <TileLayer
          url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
          attribution="&copy; Google Maps"
          maxNativeZoom={18}
          maxZoom={21}
        />
        
        {/* DEFAULT VIEW (Zoom Out) */}
        {mapZoom < 18 && (
          <Polyline 
            positions={BC_MAIN_COORDINATES} 
            pathOptions={{ color: '#43b581', weight: 5 }}
          >
            <Tooltip sticky>FO CABLE BUNDLE (A, B, C, D)</Tooltip>
          </Polyline>
        )}

        {/* DETAILED VIEW (Zoom In) */}
        {mapZoom >= 18 && (
          <>
            <Polyline 
              positions={BC_MAIN_COORDINATES.slice(9).map(p => [p[0] + 0.000025, p[1] - 0.000025])} 
              pathOptions={{ color: '#43b581', weight: 3 }}
            >
              <Tooltip sticky>CABLE A - Normal</Tooltip>
            </Polyline>

            <Polyline 
              positions={BC_MAIN_COORDINATES.slice(5).map(p => [p[0] + 0.000008, p[1] - 0.000008])} 
              pathOptions={{ color: '#eab308', weight: 3 }}
            >
              <Tooltip sticky>CABLE B - Warning</Tooltip>
            </Polyline>

            <Polyline 
              positions={BC_MAIN_COORDINATES.map(p => [p[0] - 0.000008, p[1] + 0.000008])} 
              pathOptions={{ color: '#f04747', weight: 3, className: 'animate-pulse' }}
            >
              <Tooltip sticky>CABLE C - Danger (Overheat)</Tooltip>
            </Polyline>

            <Polyline 
              positions={BC_MAIN_COORDINATES.map(p => [p[0] - 0.000025, p[1] + 0.000025])} 
              pathOptions={{ color: '#43b581', weight: 3 }}
            >
              <Tooltip sticky>CABLE D - Normal</Tooltip>
            </Polyline>
          </>
        )}

        {/* TUNNEL CONNECTIONS */}
        {TUNNEL_SENSORS.foD.map((sensor, idx) => {
          const baseProj = getClosestPointOnPath(sensor.coord, BC_MAIN_COORDINATES);
          const targetPoint = mapZoom >= 18 
            ? [baseProj[0] - 0.000025, baseProj[1] + 0.000025] as [number, number]
            : baseProj;
          return (
            <React.Fragment key={`foD-group-${idx}`}>
              <Polyline 
                positions={[sensor.coord, targetPoint]}
                pathOptions={{ color: '#43b581', weight: 3 }}
              >
                <Tooltip sticky>Tunnel connected to FO D</Tooltip>
              </Polyline>
              {/* Anchor tidak terlihat untuk tooltip */}
              <CircleMarker center={sensor.coord} radius={0} stroke={false} fillOpacity={0}>
                <Tooltip direction="bottom" offset={[0, idx % 2 === 0 ? 5 : 25]} opacity={1} permanent className="custom-tunnel-tooltip fo-d">
                  {sensor.name}
                </Tooltip>
              </CircleMarker>
            </React.Fragment>
          );
        })}

        {TUNNEL_SENSORS.foB.map((sensor, idx) => {
          const baseProj = getClosestPointOnPath(sensor.coord, BC_MAIN_COORDINATES.slice(5));
          const targetPoint = mapZoom >= 18 
            ? [baseProj[0] + 0.000008, baseProj[1] - 0.000008] as [number, number]
            : baseProj;
          return (
            <React.Fragment key={`foB-group-${idx}`}>
              <Polyline 
                positions={[sensor.coord, targetPoint]}
                pathOptions={{ color: '#eab308', weight: 3 }}
              >
                <Tooltip sticky>Tunnel connected to FO B</Tooltip>
              </Polyline>
              <CircleMarker center={sensor.coord} radius={0} stroke={false} fillOpacity={0}>
                <Tooltip direction="top" offset={[0, idx % 2 === 0 ? -5 : -25]} opacity={1} permanent className="custom-tunnel-tooltip fo-b">
                  {sensor.name}
                </Tooltip>
              </CircleMarker>
            </React.Fragment>
          );
        })}

        {TUNNEL_SENSORS.foA.map((sensor, idx) => {
          const baseProj = getClosestPointOnPath(sensor.coord, BC_MAIN_COORDINATES.slice(9));
          const targetPoint = mapZoom >= 18 
            ? [baseProj[0] + 0.000025, baseProj[1] - 0.000025] as [number, number]
            : baseProj;
          return (
            <React.Fragment key={`foA-group-${idx}`}>
              <Polyline 
                positions={[sensor.coord, targetPoint]}
                pathOptions={{ color: '#43b581', weight: 3 }}
              >
                <Tooltip sticky>Tunnel connected to FO A</Tooltip>
              </Polyline>
              <CircleMarker center={sensor.coord} radius={0} stroke={false} fillOpacity={0}>
                <Tooltip direction="top" offset={[0, idx % 2 === 0 ? -25 : -5]} opacity={1} permanent className="custom-tunnel-tooltip fo-a">
                  {sensor.name}
                </Tooltip>
              </CircleMarker>
            </React.Fragment>
          );
        })}

        {/* BC MAIN 02 */}
        <Polyline 
          positions={BC_MAIN_02_COORDINATES} 
          pathOptions={{ color: '#43b581', weight: 5 }}
        >
          <Tooltip sticky>BC MAIN 02 - FO CABLE</Tooltip>
        </Polyline>

      </MapContainer>
    </div>
  );
}
