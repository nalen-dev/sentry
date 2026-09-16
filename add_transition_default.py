import sqlite3
import os

db_path = os.path.expanduser('~/.local/share/com.sentry.app/sentry_scada.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()

query = """
INSERT OR IGNORE INTO map_calibration 
(main_group, start_m, end_m, start_svg_x, start_svg_y, end_svg_x, end_svg_y, start_lat, start_lng, end_lat, end_lng) 
VALUES ('BC4B-BC5 TRANSITION', 0, 40, 1209.0, 290.0, 1241.0, 290.0, -6.2, 106.804, -6.2, 106.805);
"""

try:
    c.execute(query)
except Exception as e:
    print(e)

conn.commit()
conn.close()
