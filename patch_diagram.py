import re

with open('src/features/map/DiagramVisualization.tsx', 'r') as f:
    content = f.read()

# Add props
props_old = """interface Props {
  isFullscreen: boolean;
  segments: LiveSegment[];
  warningThreshold: number;
  criticalThreshold: number;
}"""
props_new = """interface Props {
  isFullscreen: boolean;
  segments: LiveSegment[];
  warningThreshold: number;
  criticalThreshold: number;
  hideHeader?: boolean;
  alwaysShowPin?: boolean;
}"""
content = content.replace(props_old, props_new)

# Add destructuring for new props
sig_old = "export default function DiagramVisualization({ isFullscreen, segments, warningThreshold, criticalThreshold }: Props) {"
sig_new = "export default function DiagramVisualization({ isFullscreen, segments, warningThreshold, criticalThreshold, hideHeader, alwaysShowPin }: Props) {"
content = content.replace(sig_old, sig_new)

# Modify pin rendering in the first branch (subgroup paths)
is_alarm_cond = "const isAlarm = strokeColor.includes('red-500') || strokeColor.includes('yellow-500');"
content = content.replace(is_alarm_cond, "const isAlarm = strokeColor.includes('red-500') || strokeColor.includes('yellow-500');\n        const showPin = isAlarm || alwaysShowPin;")

# Update the conditional rendering of the pin (in both branches)
# In branch 1:
content = content.replace("{isAlarm && (\n                <g transform={`translate(${midX}, ${midY})`} className=\"animate-bounce animate-pulse\">", "{showPin && (\n                <g transform={`translate(${midX}, ${midY})`} className={isAlarm ? \"animate-bounce animate-pulse\" : \"\"}>")

# In branch 2:
content = content.replace("{isAlarm && (\n                <g transform={`translate(${midX}, ${midY})`} className=\"animate-bounce animate-pulse\">", "{showPin && (\n                <g transform={`translate(${midX}, ${midY})`} className={isAlarm ? \"animate-bounce animate-pulse\" : \"\"}>")


# Hide header if hideHeader is true
header_old = "{/* HEADER P&ID */}\n      <div className={`flex justify-between items-center mb-4 shrink-0 bg-bg-surface p-4 rounded-xl border border-border shadow-lg z-10 ${!isFullscreen ? 'ml-[400px]' : ''} transition-all duration-500`}>"
header_new = "{/* HEADER P&ID */}\n      {!hideHeader && <div className={`flex justify-between items-center mb-4 shrink-0 bg-bg-surface p-4 rounded-xl border border-border shadow-lg z-10 ${!isFullscreen ? 'ml-[400px]' : ''} transition-all duration-500`}>"
content = content.replace(header_old, header_new)

# Close the !hideHeader condition
close_header_old = """          </div>
        </div>
      </div>

      {/* SVG CANVAS */}"""
close_header_new = """          </div>
        </div>
      </div>}

      {/* SVG CANVAS */}"""
content = content.replace(close_header_old, close_header_new)

# When hideHeader is true, we probably shouldn't apply the ml-[400px] padding
canvas_old = "<div className={`flex-1 bg-bg-base border border-border rounded-xl overflow-auto custom-scrollbar relative shadow-scada-inset flex items-center justify-center ${!isFullscreen ? 'pl-[400px]' : ''} transition-all duration-500`}>"
canvas_new = "<div className={`flex-1 bg-bg-base border border-border rounded-xl overflow-auto custom-scrollbar relative shadow-scada-inset flex items-center justify-center ${(!isFullscreen && !hideHeader) ? 'pl-[400px]' : ''} transition-all duration-500`}>"
content = content.replace(canvas_old, canvas_new)


with open('src/features/map/DiagramVisualization.tsx', 'w') as f:
    f.write(content)

