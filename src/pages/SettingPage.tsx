import { useState, useEffect } from 'react';
import { 
  Settings as SettingsIcon, 
  Clock, 
  Users, 
  Database, 
  Thermometer, 
  ShieldAlert,
  Save,
  RotateCcw,
  Link2,
  Map
} from 'lucide-react';
import TopNavbar from '../components/layout/TopNavbar';
import { invoke } from '@tauri-apps/api/core';
import { useToast } from '../contexts/ToastContext';

type SettingTab = 'time' | 'mapping' | 'map-calibration' | 'users' | 'database' | 'threshold' | 'advanced';

interface UserData {
  id: string;
  role: string;
  status: string;
}

import MappingGrid, { SegmentMapping } from '../components/MappingGrid';
import ConfirmModal from '../components/ConfirmModal';


export interface MapCalibration {
  id?: number;
  main_group: string;
  start_m: number;
  end_m: number;
  start_svg_x: number;
  start_svg_y: number;
  end_svg_x: number;
  end_svg_y: number;
  start_lat?: number;
  start_lng?: number;
  end_lat?: number;
  end_lng?: number;
}

export default function SettingPage() {
  const { showToast } = useToast();
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved ? saved === 'dark' : true;
  });
  const [userRole, setUserRole] = useState('OPERATOR');
  const [userId, setUserId] = useState('OP-7729');
  
  const [activeTab, setActiveTab] = useState<SettingTab>('time');

  // Backend States
  const [users, setUsers] = useState<UserData[]>([]);
  const [mappings, setMappings] = useState<SegmentMapping[]>([]);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  
  // Local form states
  const [warningThreshold, setWarningThreshold] = useState("60.0");
  const [criticalThreshold, setCriticalThreshold] = useState("70.0");
  const [dbHost, setDbHost] = useState("127.0.0.1");
  const [dbPort, setDbPort] = useState("3306");
  const [dbName, setDbName] = useState("dts_scada_db");
  const [dbUser, setDbUser] = useState("root");
  const [dbPass, setDbPass] = useState("********");

  useEffect(() => {
    const role = localStorage.getItem('userRole');
    const id = localStorage.getItem('userId');
    if (role) setUserRole(role);
    if (id) setUserId(id);
    
    // Load Database settings & Users
    loadBackendData();
  }, []);

  const isTauri = '__TAURI_INTERNALS__' in window;

  const loadBackendData = async () => {
    if (!isTauri) {
      console.warn("Running in browser. Backend fetch bypassed.");
      return;
    }
    try {
      // 1. Fetch settings
      const settings: Record<string, string> = await invoke('get_all_settings');
      
      // Sync local form states
      if (settings['warning_threshold']) setWarningThreshold(settings['warning_threshold']);
      if (settings['critical_threshold']) setCriticalThreshold(settings['critical_threshold']);
      if (settings['db_host']) setDbHost(settings['db_host']);
      if (settings['db_port']) setDbPort(settings['db_port']);
      if (settings['db_name']) setDbName(settings['db_name']);
      if (settings['db_user']) setDbUser(settings['db_user']);
      if (settings['db_pass']) setDbPass(settings['db_pass']);

      // 2. Fetch users
      const fetchedUsers: UserData[] = await invoke('get_users');
      setUsers(fetchedUsers);

      // 3. Fetch mappings
      const fetchedMappings: SegmentMapping[] = await invoke('get_segment_mappings');

      const fetchedCalib: MapCalibration[] = await invoke('get_map_calibration');
      setCalibrations(fetchedCalib);

      setMappings(fetchedMappings);
    } catch (err) {
      console.error("Failed to load backend data:", err);
    }
  };

  const handleSyncDts = () => {
    setShowConfirmModal(true);
  };

  
  
  const addNewCalibration = () => {
    setCalibrations([
      ...calibrations,
      { main_group: 'NEW_GROUP', start_m: 0, end_m: 100, start_svg_x: 0, start_svg_y: 0, end_svg_x: 100, end_svg_y: 100 }
    ]);
  };

  const saveCalibration = async (calib: MapCalibration) => {
    try {
      setIsSavingCalib(true);
      await invoke('save_map_calibration', { calib });
      const fetched: MapCalibration[] = await invoke('get_map_calibration');
      setCalibrations(fetched);
    } catch (e) {
      console.error(e);
    } finally {
      setIsSavingCalib(false);
    }
  };

  const confirmSyncDts = async () => {
    try {
      const res: any = await invoke('sync_dts_segments');
      showToast(`Sync Complete! Found ${res.total_found} segments. Added ${res.new_added} new segments to local mapping.`, "success");
      // reload mappings
      const fetchedMappings: SegmentMapping[] = await invoke('get_segment_mappings');

      const fetchedCalib: MapCalibration[] = await invoke('get_map_calibration');
      setCalibrations(fetchedCalib);

      setMappings(fetchedMappings);
    } catch (err) {
      console.error("Failed to sync:", err);
      showToast("Error syncing DTS: " + err, "error");
    }
  };

  const handleUpdateBulkMapping = async (ids: number[], customName: string | null, mainGroup: string, startM: number | null, endM: number | null) => {
    for (const id of ids) {
      await invoke('update_segment_mapping', {
        id,
        customName,
        mainGroup,
        startM,
        endM
      });
    }
    const fetchedMappings: SegmentMapping[] = await invoke('get_segment_mappings');

      const fetchedCalib: MapCalibration[] = await invoke('get_map_calibration');
      setCalibrations(fetchedCalib);

    setMappings(fetchedMappings);
  };

  const [isTestingDb, setIsTestingDb] = useState(false);

  const [calibrations, setCalibrations] = useState<MapCalibration[]>([]);
  const [isSavingCalib, setIsSavingCalib] = useState(false);

  const [dbTestResult, setDbTestResult] = useState<string | null>(null);

  const handleTestConnection = async () => {
    setIsTestingDb(true);
    setDbTestResult(null);
    try {
      const result: string = await invoke('test_db_connection', {
        host: dbHost,
        port: dbPort,
        user: dbUser,
        pass: dbPass,
        name: dbName
      });
      setDbTestResult(result);
    } catch (err: any) {
      setDbTestResult(err.toString());
    } finally {
      setIsTestingDb(false);
    }
  };

  const handleSaveAll = async () => {
    if (!isTauri) {
      showToast("Settings cannot be saved in a normal web browser.", "error");
      return;
    }
    try {
      await invoke('save_setting', { key: 'warning_threshold', value: warningThreshold });
      await invoke('save_setting', { key: 'critical_threshold', value: criticalThreshold });
      await invoke('save_setting', { key: 'db_host', value: dbHost });
      await invoke('save_setting', { key: 'db_port', value: dbPort });
      await invoke('save_setting', { key: 'db_name', value: dbName });
      await invoke('save_setting', { key: 'db_user', value: dbUser });
      await invoke('save_setting', { key: 'db_pass', value: dbPass });
      
      showToast("Settings saved successfully!", "success");
    } catch (err) {
      console.error("Failed to save settings:", err);
      showToast("Error saving settings: " + err, "error");
    }
  };

  useEffect(() => {
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    document.documentElement.className = isDarkMode ? 'dark' : 'light';
  }, [isDarkMode]);

  const tabs = [
    { id: 'time', label: 'Time & Date', icon: Clock },
    { id: 'mapping', label: 'Segment Mapping', icon: Link2 },
    { id: 'map-calibration', label: 'Map Calibration', icon: Map },
    { id: 'users', label: 'User Management', icon: Users },
    { id: 'database', label: 'Database Connection', icon: Database },
    { id: 'threshold', label: 'Alarm Thresholds', icon: Thermometer },
    { id: 'advanced', label: 'Advanced Settings', icon: ShieldAlert },
  ];

  const activeTabConfig = tabs.find(t => t.id === activeTab);
  const ActiveIcon = activeTabConfig?.icon;

  return (
    <div className="flex flex-col h-screen bg-bg-base text-text-primary overflow-hidden font-sans">
      <TopNavbar 
        isFullscreen={false}
        isDarkMode={isDarkMode}
        setIsDarkMode={setIsDarkMode}
        userRole={userRole}
        userId={userId}
      />

      <div className="flex-1 p-6 flex flex-col md:flex-row gap-6 overflow-hidden">
        
        {/* LEFT SIDEBAR - CATEGORIES */}
        <div className="w-full md:w-64 flex flex-col shrink-0 space-y-2 overflow-y-auto custom-scrollbar">
          <div className="mb-4">
            <h2 className="text-xl font-bold tracking-widest text-text-primary flex items-center">
              <SettingsIcon className="mr-3 text-scada-primary" size={24} /> 
              SYSTEM SETTINGS
            </h2>
            <p className="text-text-secondary font-mono text-xs mt-1">Configure global parameters</p>
          </div>
          
          <div className="flex flex-col space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as SettingTab)}
                  className={`flex items-center w-full px-4 py-3 rounded-xl transition-all ${
                    isActive 
                      ? 'bg-scada-primary/10 text-scada-primary border border-scada-primary/30 shadow-sm' 
                      : 'text-text-secondary hover:bg-bg-panel hover:text-text-primary border border-transparent'
                  }`}
                >
                  <Icon size={18} className={`mr-3 ${isActive ? 'text-scada-primary' : 'text-text-secondary'}`} />
                  <span className="font-bold text-sm tracking-wider uppercase">{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* RIGHT CONTENT AREA */}
        <div className="flex-1 bg-bg-panel border border-border rounded-xl shadow-lg flex flex-col overflow-hidden relative">
          <div className="p-6 border-b border-border flex justify-between items-center bg-bg-surface/50">
            <h3 className="text-lg font-bold tracking-widest uppercase text-text-primary flex items-center">
              {ActiveIcon && <ActiveIcon size={20} className="mr-3 text-scada-primary" />}
              {activeTabConfig?.label}
            </h3>
            <div className="flex space-x-3">
              <button className="px-4 py-2 bg-bg-surface border border-border rounded-lg text-text-secondary hover:text-text-primary transition-colors flex items-center font-bold text-xs uppercase tracking-wider">
                <RotateCcw size={14} className="mr-2" /> Reset
              </button>
              <button onClick={handleSaveAll} className="px-4 py-2 bg-scada-primary/20 text-scada-primary border border-scada-primary/30 rounded-lg hover:bg-scada-primary/30 transition-colors flex items-center font-bold text-xs uppercase tracking-wider shadow-[0_0_10px_rgba(6,182,212,0.1)]">
                <Save size={14} className="mr-2" /> Save Changes
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
            
            {/* TAB CONTENT: TIME & DATE */}
            {activeTab === 'time' && (
              <div className="max-w-2xl space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-text-secondary uppercase tracking-wider">Timezone</label>
                    <select className="w-full bg-bg-surface border border-border rounded-lg p-3 text-sm text-text-primary focus:outline-none focus:border-scada-primary">
                      <option>Asia/Jakarta (GMT+7)</option>
                      <option>UTC (GMT+0)</option>
                      <option>Asia/Singapore (GMT+8)</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-text-secondary uppercase tracking-wider">Date Format</label>
                    <select className="w-full bg-bg-surface border border-border rounded-lg p-3 text-sm text-text-primary focus:outline-none focus:border-scada-primary">
                      <option>DD/MM/YYYY</option>
                      <option>MM/DD/YYYY</option>
                      <option>YYYY-MM-DD</option>
                    </select>
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-bold text-text-secondary uppercase tracking-wider">NTP Server Sync (Network Time Protocol)</label>
                  <input type="text" defaultValue="pool.ntp.org" className="w-full bg-bg-surface border border-border rounded-lg p-3 text-sm text-text-primary font-mono focus:outline-none focus:border-scada-primary" />
                  <p className="text-[10px] text-text-secondary font-mono mt-1">Leave empty to use local system time.</p>
                </div>
              </div>
            )}

            {/* TAB CONTENT: MAPPING */}
            {activeTab === 'mapping' && (
              <div className="max-w-4xl space-y-6">
                <div className="flex justify-between items-center bg-bg-surface border border-border rounded-xl p-5">
                  <div>
                    <h4 className="text-sm font-bold text-text-primary">DTS Auto-Discovery</h4>
                    <p className="text-xs text-text-secondary mt-1">Sync configured segments (AreaTables) directly from the DTS MySQL database.</p>
                  </div>
                  <button 
                    onClick={handleSyncDts}
                    className="px-4 py-2 bg-scada-primary/20 border border-scada-primary/50 text-scada-primary rounded-lg hover:bg-scada-primary/30 transition-colors font-bold text-sm"
                  >
                    SYNC FROM DTS
                  </button>
                </div>

                {mappings.length > 0 ? (
                  <MappingGrid mappings={mappings} onUpdateBulk={handleUpdateBulkMapping} />
                ) : (
                  <div className="bg-bg-surface border border-border rounded-xl p-8 text-center text-text-secondary text-sm">
                    No segments found. Please click "SYNC FROM DTS" to fetch AreaTables.
                  </div>
                )}
              </div>
            )}

            {/* TAB CONTENT: USER MANAGEMENT */}
            {activeTab === 'users' && (
              <div className="space-y-6">
                <p className="text-text-secondary font-mono text-sm">Manage access control and user privileges for the SCADA system.</p>
                <div className="bg-bg-surface border border-border rounded-xl overflow-hidden">
                  <table className="w-full text-left">
                    <thead className="bg-bg-base border-b border-border">
                      <tr>
                        <th className="p-3 text-xs font-bold text-text-secondary uppercase tracking-wider">User ID</th>
                        <th className="p-3 text-xs font-bold text-text-secondary uppercase tracking-wider">Role</th>
                        <th className="p-3 text-xs font-bold text-text-secondary uppercase tracking-wider">Status</th>
                        <th className="p-3 text-xs font-bold text-text-secondary uppercase tracking-wider text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/50">
                      {users.length > 0 ? users.map((user) => (
                        <tr key={user.id}>
                          <td className="p-3 font-mono text-sm">{user.id}</td>
                          <td className="p-3">
                            <span className={`text-xs font-bold border px-2 py-0.5 rounded ${user.role === 'ADMINISTRATOR' ? 'bg-purple-500/10 text-purple-400 border-purple-500/30' : 'bg-blue-500/10 text-blue-400 border-blue-500/30'}`}>
                              {user.role}
                            </span>
                          </td>
                          <td className="p-3"><span className={`text-xs font-bold ${user.status === 'Active' ? 'text-scada-success' : 'text-text-secondary'}`}>{user.status}</span></td>
                          <td className="p-3 text-right"><button className="text-scada-primary text-xs font-bold hover:underline">Edit</button></td>
                        </tr>
                      )) : (
                        <tr><td colSpan={4} className="p-3 text-center text-text-secondary font-mono text-xs">No users loaded from SQLite</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
                <button className="px-4 py-2 bg-bg-surface border border-border rounded-lg text-text-primary hover:text-scada-primary transition-colors text-sm font-bold">
                  + Add New User
                </button>
              </div>
            )}

            {/* TAB CONTENT: DATABASE CONNECTION */}
            {activeTab === 'database' && (
              <div className="max-w-2xl space-y-6">
                <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 mb-6 flex items-start">
                  <Database className="text-blue-400 mr-3 mt-0.5" size={20} />
                  <div>
                    <h4 className="text-sm font-bold text-blue-400">MySQL Connection Active</h4>
                    <p className="text-xs text-blue-400/70 mt-1">System is currently connected and actively logging temperature data.</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-text-secondary uppercase tracking-wider">Host Address</label>
                    <input type="text" value={dbHost} onChange={(e) => setDbHost(e.target.value)} className="w-full bg-bg-surface border border-border rounded-lg p-3 text-sm text-text-primary font-mono focus:outline-none focus:border-scada-primary" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-text-secondary uppercase tracking-wider">Port</label>
                    <input type="text" value={dbPort} onChange={(e) => setDbPort(e.target.value)} className="w-full bg-bg-surface border border-border rounded-lg p-3 text-sm text-text-primary font-mono focus:outline-none focus:border-scada-primary" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-text-secondary uppercase tracking-wider">Database Name</label>
                    <input type="text" value={dbName} onChange={(e) => setDbName(e.target.value)} className="w-full bg-bg-surface border border-border rounded-lg p-3 text-sm text-text-primary font-mono focus:outline-none focus:border-scada-primary" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-text-secondary uppercase tracking-wider">Username</label>
                    <input type="text" value={dbUser} onChange={(e) => setDbUser(e.target.value)} className="w-full bg-bg-surface border border-border rounded-lg p-3 text-sm text-text-primary font-mono focus:outline-none focus:border-scada-primary" />
                  </div>
                  <div className="space-y-2 md:col-span-2">
                    <label className="text-xs font-bold text-text-secondary uppercase tracking-wider">Password</label>
                    <input type="password" value={dbPass} onChange={(e) => setDbPass(e.target.value)} className="w-full bg-bg-surface border border-border rounded-lg p-3 text-sm text-text-primary font-mono focus:outline-none focus:border-scada-primary" />
                  </div>
                </div>
                <div className="pt-4 flex items-center space-x-4">
                  <button 
                    onClick={handleTestConnection}
                    disabled={isTestingDb}
                    className="px-4 py-2 bg-bg-surface border border-border rounded-lg text-text-primary hover:text-scada-primary transition-colors text-sm font-bold flex items-center disabled:opacity-50"
                  >
                    <RotateCcw size={16} className={`mr-2 ${isTestingDb ? 'animate-spin' : ''}`} /> 
                    {isTestingDb ? 'Testing...' : 'Test Connection'}
                  </button>
                  {dbTestResult && (
                    <span className={`text-sm font-bold ${dbTestResult.includes('successful') ? 'text-scada-success' : 'text-scada-error'}`}>
                      {dbTestResult}
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* TAB CONTENT: THRESHOLDS */}
            {activeTab === 'threshold' && (
              <div className="max-w-2xl space-y-6">
                <p className="text-text-secondary font-mono text-sm mb-4">Set global temperature boundaries. Segments exceeding these values will trigger automated visual and auditory alarms.</p>
                
                <div className="bg-bg-surface border border-border rounded-xl p-5 space-y-6">
                  <div>
                    <div className="flex justify-between mb-2">
                      <label className="text-sm font-bold text-yellow-500 uppercase flex items-center">
                        <div className="w-3 h-3 rounded-full bg-yellow-500 mr-2"></div> Warning Threshold
                      </label>
                      <span className="font-mono font-bold text-yellow-500">{warningThreshold} °C</span>
                    </div>
                    <input type="range" min="30" max="100" value={warningThreshold} onChange={(e) => setWarningThreshold(e.target.value)} className="w-full accent-yellow-500 h-2 bg-bg-base rounded-lg appearance-none cursor-pointer" />
                    <p className="text-xs text-text-secondary mt-2">Triggers 'WARN' state on map and logs warning event.</p>
                  </div>

                  <div className="h-px w-full bg-border"></div>

                  <div>
                    <div className="flex justify-between mb-2">
                      <label className="text-sm font-bold text-red-500 uppercase flex items-center">
                        <div className="w-3 h-3 rounded-full bg-red-500 mr-2 animate-pulse"></div> Critical Alarm Threshold
                      </label>
                      <span className="font-mono font-bold text-red-500">{criticalThreshold} °C</span>
                    </div>
                    <input type="range" min="30" max="100" value={criticalThreshold} onChange={(e) => setCriticalThreshold(e.target.value)} className="w-full accent-red-500 h-2 bg-bg-base rounded-lg appearance-none cursor-pointer" />
                    <p className="text-xs text-text-secondary mt-2">Triggers 'ALARM' state, activates buzzer (if hardware connected), and requires manual operator acknowledgement.</p>
                  </div>
                </div>
              </div>
            )}

            
            {/* TAB CONTENT: MAP CALIBRATION */}
            {activeTab === 'map-calibration' && (
              <div className="space-y-6">
                <div className="flex justify-between items-center mb-4">
                  <p className="text-text-secondary font-mono text-sm max-w-xl">
                    Configure physical coordinate mapping. Maps DTS distance metrics (meters) to graphical X/Y points on the P&ID diagram and Satellite coordinates.
                  </p>
                </div>
                
                <div className="bg-bg-surface border border-border rounded-xl overflow-hidden custom-scrollbar">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-text-secondary">
                      <thead className="bg-bg-base border-b border-border">
                        <tr>
                          <th className="p-4 font-bold text-text-primary tracking-wider uppercase text-xs">Conveyor Group</th>
                          <th className="p-4 font-bold text-text-primary tracking-wider uppercase text-xs">Start M</th>
                          <th className="p-4 font-bold text-text-primary tracking-wider uppercase text-xs">End M</th>
                          <th className="p-4 font-bold text-text-primary tracking-wider uppercase text-xs">Start (X,Y)</th>
                          <th className="p-4 font-bold text-text-primary tracking-wider uppercase text-xs">End (X,Y)</th>
                          <th className="p-4 font-bold text-text-primary tracking-wider uppercase text-xs text-right">Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {calibrations.map((calib, idx) => (
                          <tr key={idx} className="border-b border-border/50 hover:bg-bg-base transition-colors">
                            <td className="p-4">
                              <input type="text" value={calib.main_group} onChange={e => {
                                const newC = [...calibrations];
                                newC[idx].main_group = e.target.value;
                                setCalibrations(newC);
                              }} className="bg-bg-base border border-border rounded p-1 w-full text-text-primary font-bold text-scada-primary" placeholder="Group Name" />
                            </td>
                            <td className="p-4">
                              <input type="number" value={calib.start_m} onChange={e => {
                                const newC = [...calibrations];
                                newC[idx].start_m = parseInt(e.target.value);
                                setCalibrations(newC);
                              }} className="bg-bg-base border border-border rounded p-1 w-20 text-text-primary" />
                            </td>
                            <td className="p-4">
                              <input type="number" value={calib.end_m} onChange={e => {
                                const newC = [...calibrations];
                                newC[idx].end_m = parseInt(e.target.value);
                                setCalibrations(newC);
                              }} className="bg-bg-base border border-border rounded p-1 w-20 text-text-primary" />
                            </td>
                            <td className="p-4 space-x-2">
                              <input type="number" value={calib.start_svg_x} onChange={e => {
                                const newC = [...calibrations];
                                newC[idx].start_svg_x = parseFloat(e.target.value);
                                setCalibrations(newC);
                              }} className="bg-bg-base border border-border rounded p-1 w-16 text-text-primary" />
                              <input type="number" value={calib.start_svg_y} onChange={e => {
                                const newC = [...calibrations];
                                newC[idx].start_svg_y = parseFloat(e.target.value);
                                setCalibrations(newC);
                              }} className="bg-bg-base border border-border rounded p-1 w-16 text-text-primary" />
                            </td>
                            <td className="p-4 space-x-2">
                              <input type="number" value={calib.end_svg_x} onChange={e => {
                                const newC = [...calibrations];
                                newC[idx].end_svg_x = parseFloat(e.target.value);
                                setCalibrations(newC);
                              }} className="bg-bg-base border border-border rounded p-1 w-16 text-text-primary" />
                              <input type="number" value={calib.end_svg_y} onChange={e => {
                                const newC = [...calibrations];
                                newC[idx].end_svg_y = parseFloat(e.target.value);
                                setCalibrations(newC);
                              }} className="bg-bg-base border border-border rounded p-1 w-16 text-text-primary" />
                            </td>
                            <td className="p-4 text-right">
                              <button onClick={() => saveCalibration(calib)} className="text-xs font-bold text-scada-primary border border-scada-primary/50 hover:bg-scada-primary/10 px-3 py-1 rounded transition-colors disabled:opacity-50" disabled={isSavingCalib}>
                                Save
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div className="p-4 border-t border-border bg-bg-surface/50">
                    <button onClick={addNewCalibration} className="px-4 py-2 bg-scada-primary/20 text-scada-primary font-bold text-xs rounded hover:bg-scada-primary/30 transition-colors border border-scada-primary/50 flex items-center">
                      + Add New Calibration Area
                    </button>
                  </div>
                </div>
                
                <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-5 mt-6">
                  <h4 className="text-sm font-bold text-blue-400 mb-2">How Interpolation Works</h4>
                  <p className="text-xs text-blue-400/80 mb-2">
                    When an alarm occurs at meter <strong>M</strong> on a conveyor group, the system checks the corresponding Start/End M distance bounds above.
                  </p>
                  <p className="text-xs text-blue-400/80">
                    It calculates the percentage <code>(M - Start_M) / (End_M - Start_M)</code> and uses it to automatically plot a warning pin precisely on the SVG diagram between <strong>Start (X,Y)</strong> and <strong>End (X,Y)</strong>!
                  </p>
                </div>
              </div>
            )}

            {/* TAB CONTENT: ADVANCED */}
            {activeTab === 'advanced' && (
              <div className="space-y-6">
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-5">
                  <h4 className="text-sm font-bold text-red-400 flex items-center mb-2">
                    <ShieldAlert size={18} className="mr-2" /> Danger Zone
                  </h4>
                  <p className="text-xs text-red-400/70 mb-4">These settings can cause system instability or data loss if misconfigured.</p>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between items-center bg-bg-base p-4 rounded-lg border border-red-900/30">
                      <div>
                        <div className="font-bold text-sm text-text-primary">Purge Historical Data</div>
                        <div className="text-xs text-text-secondary mt-1">Permanently deletes all logs and chart data older than 90 days.</div>
                      </div>
                      <button className="px-4 py-2 bg-red-500/20 text-red-400 font-bold text-xs rounded hover:bg-red-500/30 transition-colors border border-red-500/50">PURGE NOW</button>
                    </div>
                    <div className="flex justify-between items-center bg-bg-base p-4 rounded-lg border border-red-900/30">
                      <div>
                        <div className="font-bold text-sm text-text-primary">Factory Reset</div>
                        <div className="text-xs text-text-secondary mt-1">Reset all configurations (thresholds, DB connection) to default.</div>
                      </div>
                      <button className="px-4 py-2 bg-red-500/20 text-red-400 font-bold text-xs rounded hover:bg-red-500/30 transition-colors border border-red-500/50">RESET SYSTEM</button>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
          </div>
        </div>
      </div>
      <ConfirmModal isOpen={showConfirmModal} title="Confirm DTS Sync" message="WARNING: Syncing will wipe all existing segment groups and aliases, replacing them with fresh data from active DTS channels. Continue?" confirmText="Yes, Wipe & Sync" cancelText="Cancel" variant="danger" onConfirm={confirmSyncDts} onCancel={() => setShowConfirmModal(false)} />
    </div>
  );
}
