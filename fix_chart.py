import re

with open('src/pages/ChartPage.tsx', 'r') as f:
    content = f.read()

# Add Activity to lucide-react imports
content = content.replace("Thermometer, Layers, Map, RefreshCw, XCircle", "Thermometer, Layers, Map, RefreshCw, XCircle, Activity")

# Add isFullscreen={false} to TopNavbar
content = content.replace("<TopNavbar \n        isDarkMode={isDarkMode}", "<TopNavbar \n        isFullscreen={false}\n        isDarkMode={isDarkMode}")

with open('src/pages/ChartPage.tsx', 'w') as f:
    f.write(content)

