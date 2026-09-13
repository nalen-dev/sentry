const fs = require('fs');
const file = 'src/pages/SettingPage.tsx';
let content = fs.readFileSync(file, 'utf8');

// inject useToast
content = content.replace('export default function SettingPage() {', 'export default function SettingPage() {\n  const { showToast } = useToast();');

// replace alerts with showToast
content = content.replace(/alert\(\`Sync Complete!(.*?)\`\);/g, 'showToast(`Sync Complete!$1`, "success");');
content = content.replace(/alert\("Error syncing DTS: " \+ err\);/g, 'showToast("Error syncing DTS: " + err, "error");');
content = content.replace(/alert\("Settings cannot be saved in a normal web browser. Please run the Tauri desktop app."\);/g, 'showToast("Settings cannot be saved in a normal web browser.", "error");');
content = content.replace(/alert\("Settings saved successfully to SQLite database!"\);/g, 'showToast("Settings saved successfully!", "success");');
content = content.replace(/alert\("Error saving settings: " \+ err\);/g, 'showToast("Error saving settings: " + err, "error");');

fs.writeFileSync(file, content);
