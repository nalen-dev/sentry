import re

with open('src/components/SegmentDetailModal.tsx', 'r') as f:
    sm = f.read()

# Replace the whole useEffect
pattern = re.compile(r"  useEffect\(\(\) => \{\n    let isMounted = true;.*?  \}, \[.*?\]\);", re.DOTALL)

new_effect = """  useEffect(() => {
    let isMounted = true;
    import('@tauri-apps/api/core').then(({ invoke }) => {
      const fetchData = async () => {
        if (!segment.dts_ch || !segment.dts_code) return;
        try {
          const data = await invoke<any[]>('get_segment_history', { dtsCh: segment.dts_ch, dtsCode: segment.dts_code, minutes: 30 });
          if (isMounted) setChartData(data);
        } catch (err) {
          console.error("Failed to fetch chart data", err);
        }
      };

      fetchData();
      const timer = setInterval(fetchData, 5000);
      return () => { isMounted = false; clearInterval(timer); };
    });
  }, [segment.dts_ch, segment.dts_code]);"""

sm = pattern.sub(new_effect, sm)

# Also ensure chartMode is totally gone
sm = re.sub(r"const \[chartMode, setChartMode\] = .*?;", "", sm)

with open('src/components/SegmentDetailModal.tsx', 'w') as f:
    f.write(sm)

