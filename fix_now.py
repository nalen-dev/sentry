import re

with open('src-tauri/src/lib.rs', 'r') as f:
    content = f.read()

# For get_groups_history
# Let's dynamically get the MAX(CreationTime) to use as the base for the filter.
# If we do WHERE CreationTime >= DATE_SUB((SELECT MAX(CreationTime) FROM fq_history_list), INTERVAL ? MINUTE)
# Wait, a subquery in WHERE without an index on the full table MAX might be slow (or very fast if indexed).
# We have idx_ch_code_time on (Ch, Code, CreationTime).

q1_old = 'AND CreationTime >= DATE_SUB(NOW(), INTERVAL ? MINUTE) ORDER BY CreationTime DESC'
q1_new = 'AND CreationTime >= DATE_SUB((SELECT MAX(CreationTime) FROM fq_history_list), INTERVAL ? MINUTE) ORDER BY CreationTime DESC'

content = content.replace(q1_old, q1_new)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(content)

