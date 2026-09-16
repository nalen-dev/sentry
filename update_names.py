import sqlite3
import os

db_path = os.path.expanduser('~/.local/share/com.sentry.app/sentry_scada.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()

queries = [
    "UPDATE map_calibration SET main_group = 'BC45-MOTOR' WHERE main_group = 'BC4B-BC5 TRANSITION';",
    "UPDATE map_calibration SET main_group = 'BEK56' WHERE main_group = 'FIBER A (TN BEK 5-6)';",
    "UPDATE map_calibration SET main_group = 'BEK34' WHERE main_group = 'FIBER B (TN BEK 3-4)';",
    "UPDATE map_calibration SET main_group = 'TCM16' WHERE main_group = 'FIBER D (TN TCM 1-6)';"
]

for q in queries:
    c.execute(q)

conn.commit()
conn.close()
