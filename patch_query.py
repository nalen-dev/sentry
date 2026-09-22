import re

with open('src-tauri/src/lib.rs', 'r') as f:
    content = f.read()

# Revert get_groups_history query
q_old = "SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? AND CreationTime >= ? AND CreationTime <= ? ORDER BY id ASC LIMIT ?"
q_new = "SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? AND CreationTime >= ? AND CreationTime <= ? ORDER BY CreationTime ASC LIMIT ?"
content = content.replace(q_old, q_new)

# Revert get_segment_history query
q2_old = "SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY id DESC LIMIT ?"
q2_new = "SELECT CreationTime, TempAvg FROM fq_history_list WHERE Ch = ? AND Code = ? ORDER BY CreationTime DESC LIMIT ?"
content = content.replace(q2_old, q2_new)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(content)

