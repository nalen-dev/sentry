import re

with open('src/lib.rs', 'r') as f:
    content = f.read()

# sync_dts_segments
pattern_sync = r'let port_num = db_port.*?let mysql_pool = sqlx::mysql::MySqlPoolOptions.*?map_err.*?;\s*'
content = re.sub(pattern_sync, r'let mysql_pool = get_mysql_pool(&state, &mysql_state).await?;\n    ', content, flags=re.DOTALL)

# get_live_segments
pattern_live = r'let port_num = db_port.*?let mysql_pool = sqlx::mysql::MySqlPoolOptions.*?map_err.*?;\s*'
content = re.sub(pattern_live, r'let mysql_pool = get_mysql_pool(&state, &mysql_state).await?;\n    ', content, flags=re.DOTALL)

# the other ones don't use port_num, they just do:
# let options = sqlx::mysql::MySqlConnectOptions::new().host(&db_host).port(db_port.parse().unwrap_or(3306)).username(&db_user).password(&db_pass).database(&db_name);
# let mysql_pool = sqlx::mysql::MySqlPoolOptions::new().max_connections(1).connect_with(options).await.map_err(|e| e.to_string())?;

pattern_others = r'let options = sqlx::mysql::MySqlConnectOptions::new.*?;\s*let mysql_pool = sqlx::mysql::MySqlPoolOptions::new.*?;\s*'
content = re.sub(pattern_others, r'let mysql_pool = get_mysql_pool(&state, &mysql_state).await?;\n    ', content, flags=re.DOTALL)

# test_db_connection
pattern_test = r'let options = sqlx::mysql::MySqlConnectOptions.*?let pool = sqlx::mysql::MySqlPoolOptions.*?map_err.*?;\s*'
# wait, test_db_connection shouldn't use the shared pool because it takes host, port, etc as arguments directly!
# I'll leave test_db_connection alone. 

with open('src/lib.rs', 'w') as f:
    f.write(content)
