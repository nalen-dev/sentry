import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    content = f.read()

# Fix History Chart
history_old = "<YAxis stroke={isDarkMode ? '#888' : '#666'} tick={{ fill: isDarkMode ? '#888' : '#666' }} domain={[0, 100]} />"
history_new = "<YAxis stroke={isDarkMode ? '#888' : '#666'} tick={{ fill: isDarkMode ? '#888' : '#666' }} domain={['auto', 'auto']} />"
content = content.replace(history_old, history_new)

# Fix Spatial Profile
spatial_old = "<YAxis stroke={isDarkMode ? '#888' : '#666'} tick={{ fill: isDarkMode ? '#888' : '#666' }} domain={[20, (dataMax: number) => Math.max(dataMax + 10, 80)]} />"
spatial_new = "<YAxis stroke={isDarkMode ? '#888' : '#666'} tick={{ fill: isDarkMode ? '#888' : '#666' }} domain={[0, 100]} />"
content = content.replace(spatial_old, spatial_new)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(content)

