import re

with open('src-tauri/src/lib.rs', 'r') as f:
    content = f.read()

# Fix fq_history_list query
old_hist_query = 'sqlx::query_as("SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? AND DATE(CreationTime) = ? ORDER BY CreationTime DESC LIMIT ?")'
new_hist_query = 'sqlx::query_as("SELECT CreationTime, TempAvg, Ch, Code FROM fq_history_list WHERE Ch = ? AND Code = ? AND CreationTime >= ? AND CreationTime < DATE_ADD(?, INTERVAL 1 DAY) ORDER BY CreationTime DESC LIMIT ?")'
content = content.replace(old_hist_query, new_hist_query)

# Fix fq_history_list binds
old_hist_binds = '.bind(map.dts_ch).bind(map.dts_code).bind(d).bind(limit)'
new_hist_binds = '.bind(map.dts_ch).bind(map.dts_code).bind(d.clone()).bind(d).bind(limit)'
content = content.replace(old_hist_binds, new_hist_binds)

# Fix alarmlog query
old_alarm_query = 'sqlx::query_as("SELECT ID, CreationTime, Ch, Code, AlarmPoint, AlarmCode, AlarmTemp, AlarmResetTime FROM alarmlog WHERE DATE(CreationTime) = ? ORDER BY CreationTime DESC LIMIT 1000")'
new_alarm_query = 'sqlx::query_as("SELECT ID, CreationTime, Ch, Code, AlarmPoint, AlarmCode, AlarmTemp, AlarmResetTime FROM alarmlog WHERE CreationTime >= ? AND CreationTime < DATE_ADD(?, INTERVAL 1 DAY) ORDER BY CreationTime DESC LIMIT 1000")'
content = content.replace(old_alarm_query, new_alarm_query)

# Fix alarmlog binds
old_alarm_binds = '.bind(d)'
new_alarm_binds = '.bind(d.clone()).bind(d)'
content = content.replace(old_alarm_binds, new_alarm_binds)

with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(content)
