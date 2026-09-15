import re

with open('src/components/SegmentDetailModal.tsx', 'r') as f:
    sm = f.read()

# Change 'dot={false}' to 'dot={true}' in Line
sm = sm.replace(
    """<Line type="monotone" dataKey="temp" stroke="var(--scada-primary)" strokeWidth={2} dot={false} activeDot={{ r: 6, fill: 'var(--scada-primary)' }} connectNulls={true} />""",
    """<Line type="monotone" dataKey="temp" stroke="var(--scada-primary)" strokeWidth={2} dot={true} activeDot={{ r: 6, fill: 'var(--scada-primary)' }} connectNulls={true} />"""
)

# Change 'Avg Temp' to 'Max Temp' (wait, the text is actually 'Avg Temp' for segment.temp_avg?)
# Let's check what the text is.
