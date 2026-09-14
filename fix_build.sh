#!/bin/bash
# Fix constants.ts
sed -i "s/temp: '37.5'/temp: 37.5, status: 'Normal'/g" src/data/constants.ts
sed -i "s/id: \`a-\${i + 1}\`/id: i + 1/g" src/data/constants.ts
sed -i "s/temp: String(35 + Math.floor(Math.random() \* 5))/temp: 35 + Math.floor(Math.random() \* 5), status: 'Normal'/g" src/data/constants.ts

# Fix DataModal duplicate toggleGroup (delete lines 57-62 probably)
sed -i '/const toggleGroup = (groupName: string) => {/,/};/d' src/features/dashboard/DataModal.tsx
