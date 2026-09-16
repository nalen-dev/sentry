import re

with open('src/pages/SettingPage.tsx', 'r') as f:
    code = f.read()

# Make main_group editable
old_main_group = """<td className="p-4">
                              <span className="font-bold text-scada-primary bg-scada-primary/10 px-2 py-1 rounded">{calib.main_group}</span>
                            </td>"""
new_main_group = """<td className="p-4">
                              <input type="text" value={calib.main_group} onChange={e => {
                                const newC = [...calibrations];
                                newC[idx].main_group = e.target.value;
                                setCalibrations(newC);
                              }} className="bg-bg-base border border-border rounded p-1 w-full text-text-primary font-bold text-scada-primary" placeholder="Group Name" />
                            </td>"""
code = code.replace(old_main_group, new_main_group)

# Add "Add New Calibration" button function
func_code = """
  const addNewCalibration = () => {
    setCalibrations([
      ...calibrations,
      { main_group: 'NEW_GROUP', start_m: 0, end_m: 100, start_svg_x: 0, start_svg_y: 0, end_svg_x: 100, end_svg_y: 100 }
    ]);
  };
"""
code = code.replace("const saveCalibration = async (calib: MapCalibration) => {", func_code + "\n  const saveCalibration = async (calib: MapCalibration) => {")

# Add the button below the table
old_table_end = """                    </table>
                  </div>
                </div>"""
new_table_end = """                    </table>
                  </div>
                  <div className="p-4 border-t border-border bg-bg-surface/50">
                    <button onClick={addNewCalibration} className="px-4 py-2 bg-scada-primary/20 text-scada-primary font-bold text-xs rounded hover:bg-scada-primary/30 transition-colors border border-scada-primary/50 flex items-center">
                      + Add New Calibration Area
                    </button>
                  </div>
                </div>"""
code = code.replace(old_table_end, new_table_end)

with open('src/pages/SettingPage.tsx', 'w') as f:
    f.write(code)

