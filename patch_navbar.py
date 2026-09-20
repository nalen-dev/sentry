import re

with open('src/components/layout/TopNavbar.tsx', 'r') as f:
    content = f.read()

# Add useEffect to imports
content = content.replace("import { useState } from 'react';", "import { useState, useEffect } from 'react';")
content = content.replace("import { Sun, Moon, Layout, History, LineChart, Settings, User, LogOut, Maximize, Minimize, Clock } from 'lucide-react';", "import { Sun, Moon, Layout, History, LineChart, Settings, User, LogOut, Maximize, Minimize, Clock } from 'lucide-react';")
if 'Clock' not in content:
    content = content.replace("Settings, User, LogOut, Maximize, Minimize }", "Settings, User, LogOut, Maximize, Minimize, Clock }")


# Add time state inside TopNavbar
state_injection = """  const [isTrueFullscreen, setIsTrueFullscreen] = useState(false);

  const [currentTime, setCurrentTime] = useState(new Date());
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);
"""
content = content.replace("  const [isTrueFullscreen, setIsTrueFullscreen] = useState(false);", state_injection)

# Replace User block
old_user_block = """        {/* LOGIN INFORMATION */}
        <div className={`flex items-center ${isFullscreen ? 'space-x-2' : 'space-x-4'}`}>
          <div className="flex items-center space-x-3 cursor-pointer hover:opacity-80 transition-opacity" title={`${userRole} (${userId})`}>
            {!isFullscreen && (
              <div className="text-right hidden sm:block">
                <div className="text-sm font-bold text-text-primary">{userRole}</div>
                <div className="text-xs text-text-secondary font-mono">ID: {userId}</div>
              </div>
            )}
            <div className="h-10 w-10 bg-bg-surface border border-border rounded-full flex items-center justify-center overflow-hidden">
              <User size={20} className="text-text-secondary" />
            </div>
          </div>"""

new_user_block = """        {/* TIME INFORMATION & LOGOUT */}
        <div className={`flex items-center ${isFullscreen ? 'space-x-2' : 'space-x-4'}`}>
          <div className="flex items-center space-x-3 cursor-pointer hover:opacity-80 transition-opacity">
            {!isFullscreen && (
              <div className="flex flex-col items-end min-w-[120px]">
                <span className="text-[10px] font-bold text-text-secondary font-mono tracking-widest uppercase">
                  {currentTime.toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })}
                </span>
                <div className="flex items-center text-scada-primary font-mono font-bold text-base mt-0.5">
                  <Clock size={14} className="mr-1.5" />
                  {currentTime.toLocaleTimeString('en-GB', { hour12: false })}
                </div>
              </div>
            )}
          </div>"""
content = content.replace(old_user_block, new_user_block)

with open('src/components/layout/TopNavbar.tsx', 'w') as f:
    f.write(content)

