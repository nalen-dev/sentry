const fs = require('fs');
const file = 'src/pages/SettingPage.tsx';
let content = fs.readFileSync(file, 'utf8');
content = content.replace(/import TopNavbar[\s\S]*?\/\/import { invoke } from '@tauri-apps\/api\/core';/m, `import TopNavbar from '../components/layout/TopNavbar';
import MappingGrid, { SegmentMapping } from '../components/MappingGrid';
import { invoke } from '@tauri-apps/api/core';
import { useToast } from '../contexts/ToastContext';`);
fs.writeFileSync(file, content);
