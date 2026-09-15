import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

# Add errorMessage state
state_block = r"  const \[hasError, setHasError\] = useState\(false\);"
new_state_block = """  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");"""
content = re.sub(state_block, new_state_block, content)

# Update fetchLive catch
fetch_old = r"          \}\)\.catch\(err => \{\n            console\.error\(\"Failed to load live data\", err\);\n            setHasError\(true\);\n            setIsLoading\(false\);\n          \}\);"
fetch_new = """          }).catch(err => {
            console.error("Failed to load live data", err);
            setHasError(true);
            setErrorMessage(typeof err === 'string' ? err : JSON.stringify(err));
            setIsLoading(false);
          });"""
content = re.sub(fetch_old, fetch_new, content)

# Update Banner
banner_old = r"CONNECTION ERROR TO DTS MYSQL\. RETRYING\.\.\."
banner_new = """CONNECTION ERROR TO DTS MYSQL. RETRYING... ({errorMessage})"""
content = re.sub(banner_old, banner_new, content)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)

