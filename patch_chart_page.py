import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    content = f.read()

# Change initial states for startTime and endTime
# Currently it's probably '' or something hardcoded

old_state = """  const [selectedDate, setSelectedDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [startTime, setStartTime] = useState('08:00');
  const [endTime, setEndTime] = useState('16:00');"""

new_state = """  const [selectedDate, setSelectedDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [startTime, setStartTime] = useState(() => {
    const d = new Date();
    d.setHours(d.getHours() - 1);
    return d.toTimeString().substring(0, 5);
  });
  const [endTime, setEndTime] = useState(() => {
    return new Date().toTimeString().substring(0, 5);
  });"""

content = content.replace(old_state, new_state)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(content)

