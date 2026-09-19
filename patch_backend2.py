import re

with open('src-tauri/src/lib.rs', 'r') as f:
    code = f.read()

# Fix get_groups_history
old_query = """let rows: Vec<HistRow> = if let Some(ref d) = date {
            sqlx::query_as("SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? AND DATE(CreationTime) = ? ORDER BY CreationTime DESC LIMIT ?")
                .bind(map.dts_ch).bind(map.dts_code).bind(d).bind(limit)
        } else {
            sqlx::query_as("SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
                .bind(map.dts_ch).bind(map.dts_code).bind(limit)
        };
        let rows: Vec<HistRow> = rows
            .fetch_all(&mysql_pool)
            .await.unwrap_or_default();"""

# I need to know exactly what is currently in lib.rs
