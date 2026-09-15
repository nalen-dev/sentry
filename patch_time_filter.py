import re

with open('src-tauri/src/lib.rs', 'r') as f:
    content = f.read()

# Change get_groups_history arguments and SQL
old_fn = """async fn get_groups_history(
    limit: i32,"""
new_fn = """async fn get_groups_history(
    minutes: i32,"""
content = content.replace(old_fn, new_fn)

old_sql = """        let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
            .bind(map.dts_ch).bind(map.dts_code).bind(limit)"""
new_sql = """        let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? AND CreationTime >= DATE_SUB(NOW(), INTERVAL ? MINUTE) ORDER BY CreationTime DESC")
            .bind(map.dts_ch).bind(map.dts_code).bind(minutes)"""
content = content.replace(old_sql, new_sql)

# Remove the artificial limit on sorted_times so it returns all minutes in the range
old_limit_check = """    // Keep only the last `limit` times globally
    if sorted_times.len() > limit as usize {
        let skip = sorted_times.len() - limit as usize;
        sorted_times = sorted_times.into_iter().skip(skip).collect();
    }"""
content = content.replace(old_limit_check, "")

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(content)

with open('src/pages/ChartPage.tsx', 'r') as f:
    content2 = f.read()

# Change frontend to pass minutes
old_invoke = """          const limit = selectedTimeRange === '30m' ? 30 : selectedTimeRange === '1h' ? 60 : selectedTimeRange === '6h' ? 360 : 30;
          const data: any[] = await invoke('get_groups_history', { limit });"""
new_invoke = """          const minutes = selectedTimeRange === '30m' ? 30 : selectedTimeRange === '1h' ? 60 : selectedTimeRange === '6h' ? 360 : 30;
          const data: any[] = await invoke('get_groups_history', { minutes });"""
content2 = content2.replace(old_invoke, new_invoke)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(content2)

