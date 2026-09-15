import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    content = f.read()

# Add hasError state
state_block = r"  const \[loading, setLoading\] = useState\(true\);\n  const \[stats, setStats\] = useState\(\{ max: 0, avg: 0, min: 0 \}\);"
new_state_block = """  const [loading, setLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [stats, setStats] = useState({ max: 0, avg: 0, min: 0 });"""
content = re.sub(state_block, new_state_block, content)

# Modify success path
success_path = r"          setStats\(\{ max: max === -999 \? 0 : max, min: min === 999 \? 0 : min, avg: count \? sum / count : 0 \}\);\n          setLoading\(false\);\n        \}"
success_new = """          setStats({ max: max === -999 ? 0 : max, min: min === 999 ? 0 : min, avg: count ? sum / count : 0 });
          setHasError(false);
          setLoading(false);
        }"""
content = re.sub(success_path, success_new, content)

# Modify catch block
catch_block = r"      \} catch \(err\) \{\n        console\.error\(err\);\n        if \(isMounted\) setLoading\(false\);\n      \}"
catch_new = """      } catch (err) {
        console.error(err);
        if (isMounted) {
          setHasError(true);
          setLoading(false);
        }
      }"""
content = re.sub(catch_block, catch_new, content)

# Modify UI check
ui_old = r"\) : \(\!loading && chartData\.length === 0\) \? \("
ui_new = """) : (!loading && !hasError && chartData.length === 0) ? ("""
content = re.sub(ui_old, ui_new, content)

# Add error UI
ui_error = """          ) : (!loading && hasError && chartData.length === 0) ? (
            <div className="flex-1 flex items-center justify-center font-mono text-red-500 tracking-widest font-bold animate-pulse text-center">
              CONNECTION ERROR.<br/>RETRYING...
            </div>
          ) : ("""
content = content.replace('          ) : (', ui_error, 1)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(content)

