import re

with open('src/components/SegmentDetailModal.tsx', 'r') as f:
    content = f.read()

# Add to interface
content = content.replace("  onRename?: (id: number, newName: string) => void;\n}", "  onRename?: (id: number, newName: string) => void;\n  warningThreshold?: number;\n  criticalThreshold?: number;\n}")

# Add to function signature
content = content.replace("export default function SegmentDetailModal({ segment, onClose, isAdmin, onRename }: SegmentDetailModalProps) {", "export default function SegmentDetailModal({ segment, onClose, isAdmin, onRename, warningThreshold = 45, criticalThreshold = 60 }: SegmentDetailModalProps) {")

with open('src/components/SegmentDetailModal.tsx', 'w') as f:
    f.write(content)

