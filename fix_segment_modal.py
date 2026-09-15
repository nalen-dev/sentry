import re

# 1. Update lib.rs get_segment_history to use minutes + hybrid logic
with open('src-tauri/src/lib.rs', 'r') as f:
    lib = f.read()

old_sh = """async fn get_segment_history(
    dts_ch: i32,
    dts_code: i32,
    limit: i32,
    state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<HistoryPoint>, String> {
    let state = get_mysql_pool(state, mysql_state).await?;
    
    let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
        .bind(dts_ch).bind(dts_code).bind(limit)
        .fetch_all(&*state).await.map_err(|e| e.to_string())?;

    let mut points = Vec::new();
    for r in rows {"""

new_sh = """async fn get_segment_history(
    dts_ch: i32,
    dts_code: i32,
    minutes: i32,
    state: tauri::State<'_, SqlitePool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<HistoryPoint>, String> {
    let state = get_mysql_pool(state, mysql_state).await?;
    
    let limit = minutes * 10;
    let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
        .bind(dts_ch).bind(dts_code).bind(limit)
        .fetch_all(&*state).await.map_err(|e| e.to_string())?;

    let mut points = Vec::new();
    if rows.is_empty() { return Ok(points); }
    let latest_time = rows[0].CreationTime.unwrap_or_default();
    let cutoff_time = latest_time - chrono::Duration::minutes(minutes as i64);

    for r in rows {
        if let Some(ct) = r.CreationTime {
            if ct < cutoff_time { continue; }
"""

lib = lib.replace(old_sh, new_sh)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(lib)

# 2. Update SegmentDetailModal.tsx to remove DISTANCE and just use TIME
with open('src/components/SegmentDetailModal.tsx', 'r') as f:
    sm = f.read()

# Replace chartMode state
sm = re.sub(
    r"const \[chartMode, setChartMode\] = useState\<'history' \| 'distance'\>\('history'\);",
    "",
    sm
)

# Replace useEffect
old_effect = """  useEffect(() => {
    let isMounted = true;
    import('@tauri-apps/api/core').then(({ invoke }) => {
      const fetchData = async () => {
        if (!segment.dts_ch || !segment.dts_code) return;
        try {
          if (chartMode === 'history') {
            const data = await invoke<any[]>('get_segment_history', { dtsCh: segment.dts_ch, dtsCode: segment.dts_code, minutes: 30 });
            if (isMounted) setChartData(data);
          } else {
            // Distance curve
            const startM = segment.start_m || 0;
            const endM = segment.end_m || 1000;
            const data = await invoke<any[]>('get_segment_curve', { dtsCh: segment.dts_ch, startM, endM });
            if (isMounted) setChartData(data);
          }
        } catch (err) {
          console.error("Failed to fetch chart data", err);
        }
      };

      fetchData();
      const timer = setInterval(fetchData, 5000);
      return () => { isMounted = false; clearInterval(timer); };
    });
  }, [segment, chartMode]);"""

new_effect = """  useEffect(() => {
    let isMounted = true;
    import('@tauri-apps/api/core').then(({ invoke }) => {
      const fetchData = async () => {
        if (!segment.dts_ch || !segment.dts_code) return;
        try {
          const data = await invoke<any[]>('get_segment_history', { dtsCh: segment.dts_ch, dtsCode: segment.dts_code, minutes: 30 });
          if (isMounted) setChartData(data);
        } catch (err) {
          console.error("Failed to fetch chart data", err);
        }
      };

      fetchData();
      const timer = setInterval(fetchData, 5000);
      return () => { isMounted = false; clearInterval(timer); };
    });
  }, [segment]);"""

sm = sm.replace(old_effect, new_effect)

# Replace chart UI header
old_ui_header = """              <div className="flex justify-between items-center mb-4">
                <span className="text-xs font-bold text-text-primary uppercase tracking-widest flex items-center"><Activity size={16} className="mr-2 text-scada-primary" /> {chartMode === 'history' ? 'Temperature vs Time (History)' : 'Temperature vs Distance (Live)'}</span>
                <div className="flex bg-bg-panel p-1 rounded-md">
                  <button onClick={() => setChartMode('history')} className={`text-[10px] px-2 py-1 rounded transition-colors ${chartMode === 'history' ? 'bg-bg-surface text-scada-primary' : 'text-text-secondary hover:text-text-primary'}`}>TIME</button>
                  <button onClick={() => setChartMode('distance')} className={`text-[10px] px-2 py-1 rounded transition-colors ${chartMode === 'distance' ? 'bg-bg-surface text-scada-primary' : 'text-text-secondary hover:text-text-primary'}`}>DISTANCE</button>
                </div>
              </div>"""

new_ui_header = """              <div className="flex justify-between items-center mb-4">
                <span className="text-xs font-bold text-text-primary uppercase tracking-widest flex items-center"><Activity size={16} className="mr-2 text-scada-primary" /> Temperature vs Time (30m)</span>
              </div>"""

sm = sm.replace(old_ui_header, new_ui_header)

# Replace chart XAxis dataKey
sm = sm.replace(
    """<XAxis dataKey={chartMode === 'history' ? 'time' : 'distance'} stroke="#9ca3af" fontSize={12} tickMargin={10} />""",
    """<XAxis dataKey="time" stroke="#9ca3af" fontSize={12} tickMargin={10} />"""
)

with open('src/components/SegmentDetailModal.tsx', 'w') as f:
    f.write(sm)


