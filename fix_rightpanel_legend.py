import re

with open('src/features/dashboard/RightPanel.tsx', 'r') as f:
    rp = f.read()

old_rp_history = """        try {
          const data: any[] = await invoke('get_groups_history', { minutes: 30 });
          if (!isMounted) return;
          
          if (data.length === 0) {
            setHistoryData([]);
            return;
          }
          
          const groupsSet = new Set<string>();
          const flatData = data.map(pt => {"""

new_rp_history = """        try {
          const [data, mappingsData] = await Promise.all([
             invoke<any[]>('get_groups_history', { minutes: 30 }),
             invoke<any[]>('get_segment_mappings')
          ]);
          if (!isMounted) return;
          
          if (data.length === 0) {
            setHistoryData([]);
            return;
          }
          
          const groupsSet = new Set<string>();
          mappingsData.forEach(m => {
            if (m.main_group && m.main_group !== 'Unassigned') {
              groupsSet.add(m.main_group);
            }
          });
          
          const flatData = data.map(pt => {"""

rp = rp.replace(old_rp_history, new_rp_history)

with open('src/features/dashboard/RightPanel.tsx', 'w') as f:
    f.write(rp)

