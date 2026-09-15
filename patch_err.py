import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    content = f.read()

# Add errorMessage state
state = r"  const \[hasError, setHasError\] = useState\(false\);"
new_state = """  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");"""
content = re.sub(state, new_state, content)

# Update catch block
catch_old = r"      \} catch \(err\) \{\n        console\.error\(err\);\n        if \(isMounted\) \{\n          setHasError\(true\);\n          setLoading\(false\);\n        \}\n      \}"
catch_new = """      } catch (err) {
        console.error(err);
        if (isMounted) {
          setHasError(true);
          setErrorMessage(typeof err === 'string' ? err : JSON.stringify(err));
          setLoading(false);
        }
      }"""
content = re.sub(catch_old, catch_new, content)

# Update UI
ui_old = r"CONNECTION ERROR\.<br/>RETRYING\.\.\."
ui_new = """CONNECTION ERROR.<br/>RETRYING...<br/><span className="text-xs text-red-400 mt-2 block">{errorMessage}</span>"""
content = content.replace(ui_old, ui_new)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(content)

