import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    content = f.read()

fetch_old = """        const [data, mappingsData] = await Promise.all([
           invoke<any[]>('get_groups_history', { startDt: start_dt, endDt: end_dt }),
           invoke<any[]>('get_segment_mappings')
        ]);"""

fetch_new = """        const [data, mappingsData, summary] = await Promise.all([
           invoke<any[]>('get_groups_history', { startDt: start_dt, endDt: end_dt }),
           invoke<any[]>('get_segment_mappings'),
           invoke<any>('get_history_summary', { startDt: start_dt, endDt: end_dt }).catch(e => { console.error(e); return null; })
        ]);
        setHistSummary(summary);"""

content = content.replace(fetch_old, fetch_new)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(content)

