import re

with open('src/features/map/MapVisualization.tsx', 'r') as f:
    content = f.read()

# I will use a regex to replace the segData assignment inside handleGroupClick
pattern = re.compile(r'const segData: SegmentData = \{.*?\};', re.DOTALL)

replacement = """const segData: SegmentData = {
        id: criticalSegment.id || 0,
        name: criticalSegment.custom_name || criticalSegment.original_name || `${groupName} Hotspot`,
        status: status,
        temp: maxTemp,
        distance: `${criticalSegment.start_m}m - ${criticalSegment.end_m}m`,
        isAlarm: isAlarm,
        group: groupName,
        temp_max: criticalSegment.temp_max,
        temp_min: criticalSegment.temp_min,
        temp_avg: criticalSegment.temp_avg,
        dts_ch: criticalSegment.dts_ch,
        dts_code: criticalSegment.dts_code,
        mainGroup: groupName,
        subGroup: criticalSegment.sub_group || undefined,
        start_m: criticalSegment.start_m || undefined,
        end_m: criticalSegment.end_m || undefined,
        original_name: criticalSegment.original_name
      };"""

content = pattern.sub(replacement, content)

with open('src/features/map/MapVisualization.tsx', 'w') as f:
    f.write(content)

