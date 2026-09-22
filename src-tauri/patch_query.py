import re

with open('src/lib.rs', 'r') as f:
    content = f.read()

# Replace get_groups_history query
q_old = "SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? AND CreationTime >= ? AND CreationTime <= ? ORDER BY CreationTime ASC LIMIT ?"
q_new = "SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? AND CreationTime >= ? AND CreationTime <= ? ORDER BY id ASC LIMIT ?"
content = content.replace(q_old, q_new)

# Replace get_segment_history query
q2_old = "SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?"
q2_new = "SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY id DESC LIMIT ?"
content = content.replace(q2_old, q2_new)

# Make sure we log errors instead of silent failure
content = content.replace(".await.unwrap_or_default();", ".await.map_err(|e| { eprintln!(\"SQL_ERR: {}\", e); e }).unwrap_or_default();")

with open('src/lib.rs', 'w') as f:
    f.write(content)

