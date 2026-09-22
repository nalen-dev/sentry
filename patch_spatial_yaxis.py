import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    content = f.read()

# Replace YAxis for Spatial Profile
y_old = "<YAxis stroke={isDarkMode ? '#888' : '#666'} tick={{ fill: isDarkMode ? '#888' : '#666' }} domain={['auto', 'auto']} />"
y_new = "<YAxis stroke={isDarkMode ? '#888' : '#666'} tick={{ fill: isDarkMode ? '#888' : '#666' }} domain={[0, 100]} />"
content = content.replace(y_old, y_new)

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(content)

