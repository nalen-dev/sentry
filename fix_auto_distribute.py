import re

with open('src/pages/SettingPage.tsx', 'r') as f:
    code = f.read()

old_loop = """  const handleUpdateBulkMapping = async (ids: number[], customName: string | null, mainGroup: string, subGroup: string | null, startM: number | null, endM: number | null) => {
    for (const id of ids) {
      await invoke('update_segment_mapping', {
        id,
        customName,
        mainGroup,
        subGroup,
        startM,
        endM
      });
    }"""

new_loop = """  const handleUpdateBulkMapping = async (ids: number[], customName: string | null, mainGroup: string, subGroup: string | null, startM: number | null, endM: number | null) => {
    // Sort IDs to ensure physical order
    const sortedIds = [...ids].sort((a, b) => a - b);
    
    for (let i = 0; i < sortedIds.length; i++) {
      const id = sortedIds[i];
      let segStart = startM;
      let segEnd = endM;
      
      // Auto-Distribute Distance if multiple segments and both bounds are provided
      if (sortedIds.length > 1 && startM !== null && endM !== null) {
        const totalDist = endM - startM;
        const step = totalDist / sortedIds.length;
        segStart = startM + (i * step);
        segEnd = startM + ((i + 1) * step);
        
        // Round to 1 decimal place to keep it clean
        segStart = Math.round(segStart * 10) / 10;
        segEnd = Math.round(segEnd * 10) / 10;
      }

      await invoke('update_segment_mapping', {
        id,
        customName,
        mainGroup,
        subGroup,
        startM: segStart,
        endM: segEnd
      });
    }"""

code = code.replace(old_loop, new_loop)

with open('src/pages/SettingPage.tsx', 'w') as f:
    f.write(code)

