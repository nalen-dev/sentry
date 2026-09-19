import re

with open('src-tauri/src/lib.rs', 'r') as f:
    code = f.read()

old_bad = """let rows: Vec<HistRow> = if let Some(ref d) = date {
            sqlx::query_as("SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? AND DATE(CreationTime) = ? ORDER BY CreationTime DESC LIMIT ?")
                .bind(map.dts_ch).bind(map.dts_code).bind(d).bind(limit)
        } else {
            sqlx::query_as("SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
                .bind(map.dts_ch).bind(map.dts_code).bind(limit)
        };
        let rows: Vec<HistRow> = rows
            .fetch_all(&mysql_pool)
            .await.unwrap_or_default();"""

new_good = """let rows: Vec<HistRow> = if let Some(ref d) = date {
            sqlx::query_as("SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? AND DATE(CreationTime) = ? ORDER BY CreationTime DESC LIMIT ?")
                .bind(map.dts_ch).bind(map.dts_code).bind(d).bind(limit)
                .fetch_all(&mysql_pool)
                .await.unwrap_or_default()
        } else {
            sqlx::query_as("SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
                .bind(map.dts_ch).bind(map.dts_code).bind(limit)
                .fetch_all(&mysql_pool)
                .await.unwrap_or_default()
        };"""

code = code.replace(old_bad, new_good)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(code)

