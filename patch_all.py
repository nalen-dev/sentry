import re

# --- 1. Fix get_segment_history in lib.rs ---
with open('src-tauri/src/lib.rs', 'r') as f:
    lib = f.read()

lib = lib.replace(
    "limit: i32,",
    "minutes: i32,"
)
lib = lib.replace(
    "ORDER BY CreationTime DESC LIMIT ?\")\n        .bind(dts_ch).bind(dts_code).bind(limit)",
    "AND CreationTime >= DATE_SUB(NOW(), INTERVAL ? MINUTE) ORDER BY CreationTime DESC\")\n        .bind(dts_ch).bind(dts_code).bind(minutes)"
)
with open('src-tauri/src/lib.rs', 'w') as f:
    f.write(lib)


# --- 2. Fix SegmentDetailModal.tsx (remove photo & fix chart args) ---
with open('src/components/SegmentDetailModal.tsx', 'r') as f:
    modal = f.read()

modal = modal.replace("limit: 30", "minutes: 30")

photo_block = r"            \{\/\* Photo Section \*\/\}\n            <div className=\"p-6 border-b border-border flex flex-col\">\n              <span className=\"text-xs font-bold text-text-secondary uppercase tracking-widest mb-3 flex items-center\"><ImageIcon size=\{14\} className=\"mr-2\" \/> Segment Photo<\/span>\n              <div className=\"w-full h-48 bg-bg-surface border-2 border-dashed border-border rounded-xl flex flex-col items-center justify-center text-text-secondary hover:text-scada-primary hover:border-scada-primary transition-colors cursor-pointer group\">\n                \{segment\.photoUrl \? \(\n                  <img src=\{segment\.photoUrl\} alt=\"Segment\" className=\"w-full h-full object-cover rounded-xl\" \/>\n                \) : \(\n                  <>\n                    <Camera size=\{32\} className=\"mb-2 group-hover:scale-110 transition-transform\" \/>\n                    <span className=\"text-sm font-bold\">Add Photo<\/span>\n                  <\/>\n                \)\}\n              <\/div>\n            <\/div>"

modal = re.sub(photo_block, "", modal)
# also remove unused icons
modal = modal.replace("Camera, ImageIcon, ", "")

with open('src/components/SegmentDetailModal.tsx', 'w') as f:
    f.write(modal)

