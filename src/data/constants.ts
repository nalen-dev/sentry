import { SegmentData } from '../components/SegmentDetailModal';

// Dummy area data based on request (increased to 42 for pagination testing)
export const DUMMY_AREAS: SegmentData[] = Array.from({ length: 42 }, (_, i) => ({
  id: i + 1,
  name: `Segment ${i + 1}`,
  distance: `${(i + 1) * 150}m`,
  temp: 35, status: "Normal",
  isAlarm: Math.random() > 0.95, // 5% chance of alarm
  group: i < 10 ? 'BC Main-01' : i < 20 ? 'BC Main-02' : i < 30 ? 'Top Feeders' : 'Bottom Feeders',
  areaLocation: `Zone ${String.fromCharCode(65 + (i % 5))}`, // Zone A, B, C...
  notes: ''
}));

export const DUMMY_LOGS = [
  { id: 1, time: '13:39:12', msg: 'System initialized successfully', type: 'info' },
  { id: 2, time: '13:40:05', msg: 'Calibration check on BC Main-01', type: 'info' },
  { id: 3, time: '13:41:22', msg: 'Warning threshold exceeded at TF3', type: 'warn' },
  { id: 4, time: '13:41:45', msg: 'Danger! Fire detected at VBF3', type: 'error' },
  { id: 5, time: '13:42:01', msg: 'User Administrator logged in', type: 'info' },
];

export const DUMMY_CHART_DATA = [
  { time: '13:00', temp: 32 },
  { time: '13:10', temp: 35 },
  { time: '13:20', temp: 40 },
  { time: '13:30', temp: 55 },
  { time: '13:40', temp: 84 }, // Spike
  { time: '13:50', temp: 62 },
  { time: '14:00', temp: 45 }
];

// Exact coordinates for FO pulls (BC MAIN to Control Room)
export const BC_MAIN_COORDINATES: [number, number][] = [
  [-0.307605, 115.857705],
  [-0.307412, 115.857963],
  [-0.307134, 115.858360],
  [-0.306937, 115.858619],
  [-0.306666, 115.859017],
  [-0.306469, 115.859277],
  [-0.306196, 115.859674],
  [-0.305998, 115.859932],
  [-0.305721, 115.860333],
  [-0.305526, 115.860586],
  [-0.305247, 115.860989],
  [-0.305050, 115.861242],
  [-0.304835, 115.861564],
  [-0.304692, 115.861764] // New extended endpoint to Control Room
];

// Coordinates for BC MAIN 02
export const BC_MAIN_02_COORDINATES: [number, number][] = [
  [-0.304668, 115.861801],
  [-0.303334, 115.863633],
  [-0.301602, 115.866023],
  [-0.300542, 115.867486],
  [-0.300477, 115.867567],
  [-0.299693, 115.868240]
];

// Tunnel Sensor Points
export interface TunnelSensor {
  coord: [number, number];
  name: string;
}

export const TUNNEL_SENSORS: { foD: TunnelSensor[], foB: TunnelSensor[], foA: TunnelSensor[] } = {
  foD: [ // Connected to FO D (Bottom / Normal)
    { coord: [-0.307698, 115.857773], name: 'TN TCM 1' },
    { coord: [-0.307223, 115.858430], name: 'TN TCM 2' },
    { coord: [-0.306736, 115.859074], name: 'TN TCM 3' },
    { coord: [-0.306292, 115.859751], name: 'TN TCM 4' },
    { coord: [-0.305826, 115.860419], name: 'TN TCM 5' },
    { coord: [-0.305307, 115.861036], name: 'TN TCM 6' }
  ],
  foB: [ // Connected to FO B (Warning)
    { coord: [-0.306241, 115.859110], name: 'TN BEK 3' },
    { coord: [-0.305751, 115.859768], name: 'TN BEK 4' }
  ],
  foA: [ // Connected to FO A (Top / Normal)
    { coord: [-0.305332, 115.860463], name: 'TN BEK 5' },
    { coord: [-0.304790, 115.861078], name: 'TN BEK 6' }
  ]
};
