import re

with open('src/pages/Dashboard.tsx', 'r') as f:
    content = f.read()

# Add warningThreshold and criticalThreshold to DataModal props
if "warningThreshold={warningThreshold}" not in content.split("<DataModal")[1]:
    old = """<DataModal 
            onClose={() => setShowDataModal(false)}
            areas={baseAreas}
            onSelectArea={handleModalSelectArea}
          />"""
    new = """<DataModal 
            onClose={() => setShowDataModal(false)}
            areas={baseAreas}
            onSelectArea={handleModalSelectArea}
            warningThreshold={warningThreshold}
            criticalThreshold={criticalThreshold}
          />"""
    content = content.replace(old, new)

# Add them to SegmentDetailModal props
old_seg = """<SegmentDetailModal 
          segment={selectedSegment}
          onClose={() => setSelectedSegment(null)}
        />"""
new_seg = """<SegmentDetailModal 
          segment={selectedSegment}
          onClose={() => setSelectedSegment(null)}
          warningThreshold={warningThreshold}
          criticalThreshold={criticalThreshold}
        />"""
content = content.replace(old_seg, new_seg)

with open('src/pages/Dashboard.tsx', 'w') as f:
    f.write(content)


# Update DataModal.tsx
with open('src/features/dashboard/DataModal.tsx', 'r') as f:
    data_modal = f.read()
data_modal = data_modal.replace(
    "onSelectArea: (area: any) => void;\n}",
    "onSelectArea: (area: any) => void;\n  warningThreshold?: number;\n  criticalThreshold?: number;\n}"
)
data_modal = data_modal.replace(
    "export default function DataModal({ onClose, areas, onSelectArea }: DataModalProps) {",
    "export default function DataModal({ onClose, areas, onSelectArea, warningThreshold = 45, criticalThreshold = 60 }: DataModalProps) {"
)
# Pass them to SegmentDetailModal inside DataModal if it uses it. (It doesn't render SegmentDetailModal, it just calls onSelectArea)
with open('src/features/dashboard/DataModal.tsx', 'w') as f:
    f.write(data_modal)


# Update SegmentDetailModal.tsx
with open('src/components/SegmentDetailModal.tsx', 'r') as f:
    seg_modal = f.read()
seg_modal = seg_modal.replace(
    "onClose: () => void;\n}",
    "onClose: () => void;\n  warningThreshold?: number;\n  criticalThreshold?: number;\n}"
)
seg_modal = seg_modal.replace(
    "export default function SegmentDetailModal({ segment, onClose }: SegmentDetailModalProps) {",
    "export default function SegmentDetailModal({ segment, onClose, warningThreshold = 45, criticalThreshold = 60 }: SegmentDetailModalProps) {"
)
seg_modal = seg_modal.replace(
    "warningThreshold={45}\n                        criticalThreshold={60}",
    "warningThreshold={warningThreshold}\n                        criticalThreshold={criticalThreshold}"
)
with open('src/components/SegmentDetailModal.tsx', 'w') as f:
    f.write(seg_modal)

