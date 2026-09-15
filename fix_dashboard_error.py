import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

# Add error state
state_block = r"  const \[mappings, setMappings\] = useState<LiveSegment\[\]>\(\[\]\);\n  const \[alarms, setAlarms\] = useState<AlarmLog\[\]>\(\[\]\);\n  const \[isLoading, setIsLoading\] = useState\(true\);"
new_state_block = """  const [mappings, setMappings] = useState<LiveSegment[]>([]);
  const [alarms, setAlarms] = useState<AlarmLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);"""
content = re.sub(state_block, new_state_block, content)

# Update fetchLive
fetch_old = r"          Promise\.all\(\[\n            invoke<LiveSegment\[\]>\('get_live_segments'\),\n            invoke<AlarmLog\[\]>\('get_alarms'\)\n          \]\)\.then\(\(\[m, a\]\) => \{\n            setMappings\(m\);\n            setAlarms\(a\);\n            setIsLoading\(false\);\n          \}\)\.catch\(err => \{\n            console\.error\(\"Failed to load live data\", err\);\n            setIsLoading\(false\);\n          \}\);"
fetch_new = """          Promise.all([
            invoke<LiveSegment[]>('get_live_segments'),
            invoke<AlarmLog[]>('get_alarms')
          ]).then(([m, a]) => {
            setMappings(m);
            setAlarms(a);
            setHasError(false);
            setIsLoading(false);
          }).catch(err => {
            console.error("Failed to load live data", err);
            setHasError(true);
            setIsLoading(false);
          });"""
content = re.sub(fetch_old, fetch_new, content)

# Fix empty state check
# Find: `{!isLoading && mappings.length === 0 && (`
empty_state_old = r"\{!isLoading && mappings\.length === 0 && \("
empty_state_new = """{!isLoading && !hasError && mappings.length === 0 && ("""
content = re.sub(empty_state_old, empty_state_new, content)

# Also let's show a reconnecting overlay if there is an error but we don't have mappings yet
# Or maybe just show an error toast. Actually, if we have mappings=0 and error=true, the screen will be empty map.
# Let's add a small error banner at the top if hasError is true.
banner = """
      {/* MAIN CONTENT AREA */}
      <div className="flex-1 relative overflow-hidden bg-bg-base flex">
        
        {hasError && (
          <div className="absolute top-0 left-0 right-0 z-50 bg-red-500/90 text-white text-xs font-bold font-mono tracking-widest text-center py-1">
            CONNECTION ERROR TO DTS MYSQL. RETRYING...
          </div>
        )}"""
        
content = content.replace('      {/* MAIN CONTENT AREA */}\n      <div className="flex-1 relative overflow-hidden bg-bg-base flex">', banner)


with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)

