#!/bin/bash
sed -i "s/temp: '37.5'/temp: 37.5, status: 'Normal'/g" src/data/constants.ts
