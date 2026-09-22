import re

with open('src/features/dashboard/RightPanel.tsx', 'r') as f:
    content = f.read()

# Replace the previous bad replacement
old_call = """invoke<any[]>('get_groups_history', { 
               startDt: new Date(Date.now() - 30 * 60000).toISOString().replace('T', ' ').substring(0, 19), 
               endDt: new Date().toISOString().replace('T', ' ').substring(0, 19) 
             }),"""

new_call = """invoke<any[]>('get_groups_history', { 
               startDt: (new Date(Date.now() - 30 * 60000)).toLocaleString('sv').replace('T', ' ').substring(0, 19), 
               endDt: (new Date()).toLocaleString('sv').replace('T', ' ').substring(0, 19) 
             }),"""

content = content.replace(old_call, new_call)

with open('src/features/dashboard/RightPanel.tsx', 'w') as f:
    f.write(content)

