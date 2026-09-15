import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    content = f.read()

# Replace the fetching and slicing logic in Spatial Mode
old_logic = """          const curve: any[] = await invoke('get_segment_curve', { dts_ch: ch });
          
          if (!isMounted) return;
          
          if (curve.length === 0) {
            setSpatialData([]);
            setHasError(false);
            setLoading(false);
            return;
          }
          
          // Slice the curve
          const safeMin = minM === 999999 ? 0 : minM;
          const safeMax = maxM === 0 ? curve.length : maxM;
          
          const sliced = curve.filter(pt => pt.distance >= safeMin && pt.distance <= safeMax);"""

new_logic = """          const safeMin = minM === 999999 ? 0 : minM;
          const safeMax = maxM === 0 ? 999999 : maxM;
          
          const curve: any[] = await invoke('get_segment_curve', { dts_ch: ch, start_m: safeMin, end_m: safeMax });
          
          if (!isMounted) return;
          
          if (curve.length === 0) {
            setSpatialData([]);
            setHasError(false);
            setLoading(false);
            return;
          }
          
          // Filter out error codes from Rust (< 0)
          const sliced = curve.filter(pt => pt.temp >= 0);"""

content = content.replace(old_logic, new_logic)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(content)

