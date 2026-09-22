import re

with open('src-tauri/src/db.rs', 'r') as f:
    content = f.read()

sys_log_sql = """
    sqlx::query(
        "CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT NOT NULL,
            message TEXT NOT NULL
        );"
    )
    .execute(&pool)
    .await?;
"""

if "system_logs" not in content:
    # insert before CREATE TABLE IF NOT EXISTS segment_mappings
    content = content.replace('sqlx::query(\n        "CREATE TABLE IF NOT EXISTS segment_mappings', sys_log_sql + '\n    sqlx::query(\n        "CREATE TABLE IF NOT EXISTS segment_mappings')

with open('src-tauri/src/db.rs', 'w') as f:
    f.write(content)

