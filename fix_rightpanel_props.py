import re

with open('src/features/dashboard/RightPanel.tsx', 'r') as f:
    rp = f.read()

rp = rp.replace("import { Activity, LineChart as LineChartIcon } from 'lucide-react';", "import { LineChart as LineChartIcon } from 'lucide-react';")

# Replace RightPanelProps
old_props = """interface RightPanelProps {
  totalSegments: number;
  normalSegments: number;
  warningSegments: number;
  dangerSegments: number;
  filteredAreas: any[];
}

export default function RightPanel({
  totalSegments,
  normalSegments,
  warningSegments,
  dangerSegments,
}: RightPanelProps) {"""

new_props = """interface RightPanelProps {}

export default function RightPanel({}: RightPanelProps = {}) {"""

rp = rp.replace(old_props, new_props)

with open('src/features/dashboard/RightPanel.tsx', 'w') as f:
    f.write(rp)

