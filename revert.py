import re

with open('src-tauri/src/lib.rs', 'r') as f:
    lib = f.read()

# Revert get_groups_history
old_q1 = """async fn get_groups_history(
    minutes: i32,"""
new_q1 = """async fn get_groups_history(
    limit: i32,"""
lib = lib.replace(old_q1, new_q1)

old_sql1 = """        let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? AND CreationTime >= DATE_SUB((SELECT MAX(CreationTime) FROM fq_history_list), INTERVAL ? MINUTE) ORDER BY CreationTime DESC")
            .bind(map.dts_ch).bind(map.dts_code).bind(minutes)"""
new_sql1 = """        let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
            .bind(map.dts_ch).bind(map.dts_code).bind(limit)"""
lib = lib.replace(old_sql1, new_sql1)

# Revert get_segment_history
old_q2 = """async fn get_segment_history(
    dts_ch: i32,
    dts_code: i32,
    minutes: i32,"""
new_q2 = """async fn get_segment_history(
    dts_ch: i32,
    dts_code: i32,
    limit: i32,"""
lib = lib.replace(old_q2, new_q2)

old_sql2 = """    let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? AND CreationTime >= DATE_SUB((SELECT MAX(CreationTime) FROM fq_history_list), INTERVAL ? MINUTE) ORDER BY CreationTime DESC")
        .bind(dts_ch).bind(dts_code).bind(minutes)"""
new_sql2 = """    let rows: Vec<HistRow> = sqlx::query_as("SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?")
        .bind(dts_ch).bind(dts_code).bind(limit)"""
lib = lib.replace(old_sql2, new_sql2)


with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(lib)

