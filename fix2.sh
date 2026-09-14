#!/bin/bash
sed -i "s/temp: String(35 + Math.floor(Math.random() \* 5))/temp: 35 + Math.floor(Math.random() \* 5)/g" src/data/constants.ts
sed -i "s/isAlarm: Math.random() > 0.8/isAlarm: Math.random() > 0.8, status: 'Normal'/g" src/data/constants.ts
