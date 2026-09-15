import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    db = f.read()

db = db.replace(
"""        mappingId: m.id,
        original_name: m.original_name,
        dts_ch: m.dts_ch,
        dts_code: m.dts_code,
        start_m: m.start_m ?? undefined,
        end_m: m.end_m ?? undefined,
      }));""",
"""        mappingId: m.id,
        original_name: m.original_name,
        dts_ch: m.dts_ch,
        dts_code: m.dts_code,
        start_m: m.start_m ?? undefined,
        end_m: m.end_m ?? undefined,
      };
  });"""
)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(db)

