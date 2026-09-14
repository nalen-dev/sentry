#!/bin/bash
sed -i 's/id: `A-\${i + 1}`/id: i + 1/g' src/data/constants.ts
sed -i 's/temp: (30 + Math.random() \* 20).toFixed(1)/temp: 35, status: "Normal"/g' src/data/constants.ts
