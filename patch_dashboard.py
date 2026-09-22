import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

# Make sure MapVisualization gets setSelectedSegment
old_map = """            <MapVisualization 
              isFullscreen={isFullscreen} 
              mapZoom={mapZoom} 
              setMapZoom={setMapZoom} 
              segments={mappings}
              warningThreshold={Number(warningThreshold)}
              criticalThreshold={Number(criticalThreshold)}
            />"""

new_map = """            <MapVisualization 
              isFullscreen={isFullscreen} 
              mapZoom={mapZoom} 
              setMapZoom={setMapZoom} 
              segments={mappings}
              warningThreshold={Number(warningThreshold)}
              criticalThreshold={Number(criticalThreshold)}
              setSelectedSegment={setSelectedSegment}
            />"""

content = content.replace(old_map, new_map)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)

