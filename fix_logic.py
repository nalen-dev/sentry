import re

with open('src-tauri/src/lib.rs', 'r') as f:
    lib = f.read()

# Fix get_groups_history
old_gh = """async fn get_groups_history(
    limit: i32,
    state: tauri::State<'_, MysqlPool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<GroupHistoryPoint>, String> {
    let state = get_mysql_pool(state, mysql_state).await?;
    
    let mappings: Vec<crate::domain::app_models::SegmentMapping> = sqlx::query_as("SELECT * FROM segment_mappings WHERE main_group != 'Unassigned'")
        .fetch_all(&*state).await.map_err(|e| e.to_string())?;
        
    let mut group_data: HashMap<String, HashMap<String, Vec<f32>>> = HashMap::new();
    let mut all_times: std::collections::HashSet<String> = std::collections::HashSet::new();

    for map in mappings {
        let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
            .bind(map.dts_ch).bind(map.dts_code).bind(limit)
            .fetch_all(&*state).await.unwrap_or_default();

        for r in rows {"""

new_gh = """async fn get_groups_history(
    minutes: i32,
    state: tauri::State<'_, MysqlPool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<GroupHistoryPoint>, String> {
    let state = get_mysql_pool(state, mysql_state).await?;
    
    let mappings: Vec<crate::domain::app_models::SegmentMapping> = sqlx::query_as("SELECT * FROM segment_mappings WHERE main_group != 'Unassigned'")
        .fetch_all(&*state).await.map_err(|e| e.to_string())?;
        
    let mut group_data: HashMap<String, HashMap<String, Vec<f32>>> = HashMap::new();
    let mut all_times: std::collections::HashSet<String> = std::collections::HashSet::new();
    
    let limit = minutes * 10; // safe buffer for 10-second polling

    for map in mappings {
        let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
            .bind(map.dts_ch).bind(map.dts_code).bind(limit)
            .fetch_all(&*state).await.unwrap_or_default();

        if rows.is_empty() { continue; }
        let latest_time = rows[0].CreationTime.unwrap_or_default();
        let cutoff_time = latest_time - chrono::Duration::minutes(minutes as i64);

        for r in rows {
            if let Some(ct) = r.CreationTime {
                if ct < cutoff_time { continue; }
"""
lib = lib.replace(old_gh, new_gh)

# Fix get_segment_history
old_sh = """async fn get_segment_history(
    dts_ch: i32,
    dts_code: i32,
    limit: i32,
    state: tauri::State<'_, MysqlPool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<GroupHistoryPoint>, String> {
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
    state: tauri::State<'_, MysqlPool>, mysql_state: tauri::State<'_, MysqlState>
) -> Result<Vec<GroupHistoryPoint>, String> {
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

# 2. Fix Frontend to pass minutes instead of limit
with open('src/pages/ChartPage.tsx', 'r') as f:
    cp = f.read()
cp = cp.replace(
    "const limit = selectedTimeRange === '30m' ? 180 : selectedTimeRange === '1h' ? 360 : selectedTimeRange === '6h' ? 2160 : 180;\n          const data: any[] = await invoke('get_groups_history', { limit });",
    "const minutes = selectedTimeRange === '30m' ? 30 : selectedTimeRange === '1h' ? 60 : selectedTimeRange === '6h' ? 360 : 30;\n          const data: any[] = await invoke('get_groups_history', { minutes });"
)
# Fix ChartPage Line breaking by adding connectNulls={true}
cp = cp.replace(
    """<Line key={name} type="monotone" dataKey={name} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={false} activeDot={{ r: 6, strokeWidth: 0 }} />""",
    """<Line key={name} type="monotone" dataKey={name} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={false} activeDot={{ r: 6, strokeWidth: 0 }} connectNulls={true} />"""
)
# Fix YAxis domain to 0-100
cp = cp.replace(
    """<YAxis stroke="#9ca3af" fontSize={12} domain={['dataMin - 5', 'dataMax + 5']} />""",
    """<YAxis stroke="#9ca3af" fontSize={12} domain={[0, 100]} />"""
)
with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(cp)


# Fix RightPanel
with open('src/features/dashboard/RightPanel.tsx', 'r') as f:
    rp = f.read()
rp = rp.replace("limit: 180", "minutes: 30")
rp = rp.replace(
    """<Line key={name} type="monotone" dataKey={name} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={false} activeDot={{ r: 4, strokeWidth: 0 }} />""",
    """<Line key={name} type="monotone" dataKey={name} stroke={COLORS[i % COLORS.length]} strokeWidth={2} dot={false} activeDot={{ r: 4, strokeWidth: 0 }} connectNulls={true} />"""
)
rp = rp.replace(
    """<YAxis stroke="#9ca3af" fontSize={10} domain={['dataMin - 5', 'dataMax + 5']} />""",
    """<YAxis stroke="#9ca3af" fontSize={10} domain={[0, 100]} />"""
)
with open('src/features/dashboard/RightPanel.tsx', 'w') as f:
    f.write(rp)


# Fix SegmentDetailModal
with open('src/components/SegmentDetailModal.tsx', 'r') as f:
    sm = f.read()
sm = sm.replace("limit: 180", "minutes: 30")
sm = sm.replace(
    """<Line type="monotone" dataKey="temp" stroke="var(--scada-primary)" strokeWidth={2} dot={false} activeDot={{ r: 6, fill: 'var(--scada-primary)' }} />""",
    """<Line type="monotone" dataKey="temp" stroke="var(--scada-primary)" strokeWidth={2} dot={false} activeDot={{ r: 6, fill: 'var(--scada-primary)' }} connectNulls={true} />"""
)
sm = sm.replace(
    """<YAxis stroke="#9ca3af" fontSize={12} domain={['dataMin - 10', 'dataMax + 10']} />""",
    """<YAxis stroke="#9ca3af" fontSize={12} domain={[0, 100]} />"""
)
with open('src/components/SegmentDetailModal.tsx', 'w') as f:
    f.write(sm)


