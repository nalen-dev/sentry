import re

with open('src/pages/SettingPage.tsx', 'r') as f:
    code = f.read()

# Add MapCalibration interface
interface_code = """
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
"""
code = code.replace("export interface SegmentMapping {", interface_code + "\nexport interface SegmentMapping {")

# Add map calibrations state
state_code = """
  const [calibrations, setCalibrations] = useState<MapCalibration[]>([]);
  const [isSavingCalib, setIsSavingCalib] = useState(false);
"""
code = code.replace("const [isTestingDb, setIsTestingDb] = useState(false);", "const [isTestingDb, setIsTestingDb] = useState(false);\n" + state_code)

# Add fetch call inside loadSettings
fetch_code = """
      const fetchedCalib: MapCalibration[] = await invoke('get_map_calibration');
      setCalibrations(fetchedCalib);
"""
code = code.replace("const fetchedMappings: SegmentMapping[] = await invoke('get_segment_mappings');", "const fetchedMappings: SegmentMapping[] = await invoke('get_segment_mappings');\n" + fetch_code)

# Add Save function for calibration
save_func = """
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
"""
code = code.replace("const confirmSyncDts = async () => {", save_func + "\n  const confirmSyncDts = async () => {")

# Add Icon import
code = code.replace("ShieldAlert, Link2, RotateCcw }", "ShieldAlert, Link2, RotateCcw, Map }")

# Add Tab Button
tab_button = """
              <button onClick={() => setActiveTab('mapping')} className={`w-full flex items-center p-3 rounded-lg text-sm font-bold transition-all ${activeTab === 'mapping' ? 'bg-scada-primary text-black' : 'text-text-secondary hover:bg-bg-surface'}`}><GitMerge size={18} className="mr-3" /> Area Mapping</button>
              <button onClick={() => setActiveTab('map-calibration')} className={`w-full flex items-center p-3 rounded-lg text-sm font-bold transition-all ${activeTab === 'map-calibration' ? 'bg-scada-primary text-black' : 'text-text-secondary hover:bg-bg-surface'}`}><Map size={18} className="mr-3" /> Map Calibration</button>
"""
code = code.replace("""<button onClick={() => setActiveTab('mapping')} className={`w-full flex items-center p-3 rounded-lg text-sm font-bold transition-all ${activeTab === 'mapping' ? 'bg-scada-primary text-black' : 'text-text-secondary hover:bg-bg-surface'}`}><GitMerge size={18} className="mr-3" /> Area Mapping</button>""", tab_button)

# Add Tab Content for map-calibration
tab_content = """
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
                              <span className="font-bold text-scada-primary bg-scada-primary/10 px-2 py-1 rounded">{calib.main_group}</span>
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
"""

code = code.replace("{/* TAB CONTENT: ADVANCED */}", tab_content + "\n            {/* TAB CONTENT: ADVANCED */}")

with open('src/pages/SettingPage.tsx', 'w') as f:
    f.write(code)

