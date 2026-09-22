import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    content = f.read()

# Replace filterStartTime and filterEndTime
old_start = "const [filterStartTime, setFilterStartTime] = useState<string>('08:00');"
new_start = """const [filterStartTime, setFilterStartTime] = useState<string>(() => {
    const d = new Date();
    d.setHours(d.getHours() - 1);
    return d.toTimeString().substring(0, 5);
  });"""

old_end = "const [filterEndTime, setFilterEndTime] = useState<string>('16:00');"
new_end = """const [filterEndTime, setFilterEndTime] = useState<string>(() => {
    return new Date().toTimeString().substring(0, 5);
  });"""

content = content.replace(old_start, new_start)
content = content.replace(old_end, new_end)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(content)

