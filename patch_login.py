import re

with open('src/pages/Login.tsx', 'r') as f:
    content = f.read()

if "import { invoke } from '@tauri-apps/api/core';" not in content:
    content = content.replace("import { useNavigate } from 'react-router-dom';", "import { useNavigate } from 'react-router-dom';\nimport { invoke } from '@tauri-apps/api/core';")

login_old = """  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (username === 'admin') {
      localStorage.setItem('userRole', 'ADMINISTRATOR');
      localStorage.setItem('userId', 'AD-001');
      navigate('/');
    } else if (username === 'operator') {
      localStorage.setItem('userRole', 'OPERATOR');
      localStorage.setItem('userId', 'OP-7729');
      navigate('/');
    } else {
      setError(true);
      setTimeout(() => setError(false), 3000);
    }
  };"""

login_new = """  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (username === 'admin') {
      localStorage.setItem('userRole', 'ADMINISTRATOR');
      localStorage.setItem('userId', 'AD-001');
      try {
        await invoke('write_system_log', { eventType: 'AUTH', message: 'User AD-001 (ADMINISTRATOR) berhasil login.' });
      } catch (err) { console.error(err); }
      navigate('/');
    } else if (username === 'operator') {
      localStorage.setItem('userRole', 'OPERATOR');
      localStorage.setItem('userId', 'OP-7729');
      try {
        await invoke('write_system_log', { eventType: 'AUTH', message: 'User OP-7729 (OPERATOR) berhasil login.' });
      } catch (err) { console.error(err); }
      navigate('/');
    } else {
      setError(true);
      setTimeout(() => setError(false), 3000);
    }
  };"""

content = content.replace(login_old, login_new)

with open('src/pages/Login.tsx', 'w') as f:
    f.write(content)

