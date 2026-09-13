const fs = require('fs');
const file = 'src/components/MappingGrid.tsx';
let content = fs.readFileSync(file, 'utf8');

content = content.replace("import { Save, CheckSquare, Info } from 'lucide-react';", "import { Save, CheckSquare, Info } from 'lucide-react';\nimport { useToast } from '../contexts/ToastContext';");
content = content.replace("export default function MappingGrid({ mappings, onUpdateBulk }: MappingGridProps) {", "export default function MappingGrid({ mappings, onUpdateBulk }: MappingGridProps) {\n  const { showToast } = useToast();");

const oldSave = `  const handleSave = async () => {
    if (selectedIds.size === 0) return;
    
    await onUpdateBulk(
      Array.from(selectedIds), 
      selectedIds.size === 1 ? (formCustomName || null) : null, // only allow custom name on single select
      formMainGroup, 
      formSubGroup || null
    );
    
    // Don't clear selection, let user see updates
  };`;

const newSave = `  const handleSave = async () => {
    if (selectedIds.size === 0) return;
    
    try {
      await onUpdateBulk(
        Array.from(selectedIds), 
        selectedIds.size === 1 ? (formCustomName || null) : null,
        formMainGroup, 
        formSubGroup || null
      );
      showToast(\`Successfully updated \${selectedIds.size} segments!\`, 'success');
    } catch (e) {
      showToast(\`Failed to update segments\`, 'error');
    }
  };`;

content = content.replace(oldSave, newSave);
fs.writeFileSync(file, content);
