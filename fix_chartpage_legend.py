import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    cp = f.read()

# Add get_segment_mappings call inside fetchData history mode
old_history_fetch = """        if (chartMode === 'history') {
          const minutes = selectedTimeRange === '30m' ? 30 : selectedTimeRange === '1h' ? 60 : selectedTimeRange === '6h' ? 360 : 30;
          const data: any[] = await invoke('get_groups_history', { minutes });
          
          if (!isMounted) return;
          
          if (data.length === 0) {
            setHistData([]);
            setHasError(false);
            setLoading(false);
            return;
          }
          
          const groupsSet = new Set<string>();
          const flatData = data.map(pt => {"""

new_history_fetch = """        if (chartMode === 'history') {
          const minutes = selectedTimeRange === '30m' ? 30 : selectedTimeRange === '1h' ? 60 : selectedTimeRange === '6h' ? 360 : 30;
          const [data, mappingsData] = await Promise.all([
             invoke<any[]>('get_groups_history', { minutes }),
             invoke<any[]>('get_segment_mappings')
          ]);
          
          if (!isMounted) return;
          
          if (data.length === 0) {
            setHistData([]);
            setHasError(false);
            setLoading(false);
            return;
          }
          
          const groupsSet = new Set<string>();
          mappingsData.forEach(m => {
            if (m.main_group && m.main_group !== 'Unassigned') {
              groupsSet.add(m.main_group);
            }
          });
          
          const flatData = data.map(pt => {"""

cp = cp.replace(old_history_fetch, new_history_fetch)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(cp)

