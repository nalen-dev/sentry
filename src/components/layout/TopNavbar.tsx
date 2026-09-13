import { Sun, Moon, Layout, History, LineChart, Settings, User, LogOut, Maximize, Minimize } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';

interface TopNavbarProps {
  isFullscreen: boolean;
  isDarkMode: boolean;
  setIsDarkMode: (val: boolean) => void;
  userId: string;
  userRole: string;
}

import { invoke } from '@tauri-apps/api/core';

export default function TopNavbar({ 
  isFullscreen, 
  isDarkMode, 
  setIsDarkMode,
  userId,
  userRole
}: TopNavbarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const [isTrueFullscreen, setIsTrueFullscreen] = useState(false);

  // Note: We cannot easily check initial fullscreen without invoke, so we'll just assume false initially.
  
  const toggleOSFullscreen = async () => {
    if ('__TAURI_INTERNALS__' in window) {
      try {
        const newState = await invoke<boolean>('toggle_fullscreen');
        setIsTrueFullscreen(newState);
      } catch (err) {
        console.error("Failed to toggle fullscreen:", err);
      }
    } else {
      // Browser fallback
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().then(() => setIsTrueFullscreen(true));
      } else {
        document.exitFullscreen().then(() => setIsTrueFullscreen(false));
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('userId');
    localStorage.removeItem('userRole');
    navigate('/login');
  };

  const getTabClass = (path: string) => {
    const isActive = location.pathname === path;
    const baseClass = "font-bold transition-colors flex items-center tracking-widest";
    
    if (isFullscreen) {
      return `${baseClass} p-2 rounded-lg ${isActive ? 'bg-scada-primary/10 text-scada-primary' : 'text-text-secondary hover:bg-bg-surface hover:text-text-primary'}`;
    }
    
    return `${baseClass} text-sm ${isActive ? 'text-scada-primary' : 'text-text-secondary hover:text-text-primary'}`;
  };

  return (
    <header className={`z-40 flex items-center transition-all duration-300 ${
      isFullscreen 
        ? 'absolute top-4 left-1/2 transform -translate-x-1/2 h-14 bg-bg-panel/90 backdrop-blur-md border rounded-2xl px-4 space-x-4' 
        : 'h-16 bg-bg-panel border-b px-6 shrink-0 justify-between w-full'
    }`}>
      
      {/* TITLE */}
      <div className="flex items-center">
        <div className="flex items-center">
          <img src="/sentry-logo-noname.jpg" alt="SENTRY" className={`w-auto object-contain rounded-md transition-all duration-500 ${isFullscreen ? 'h-8 mr-0' : 'h-10 mr-3'}`} />
          {!isFullscreen && (
            <div>
              <h1 className="text-xl font-bold text-text-primary tracking-widest uppercase flex items-center">
                SENTRY SCADA
              </h1>
              <p className="text-xs text-text-secondary font-mono">DTS MONITORING MODULE</p>
            </div>
          )}
        </div>
      </div>
      
      {/* NAVIGATION & USER */}
      <div className={`flex items-center ${isFullscreen ? 'space-x-2' : 'space-x-6'}`}>
        
        <nav className={`flex items-center ${isFullscreen ? 'space-x-2' : 'space-x-6 mr-4'}`}>
          <button onClick={() => navigate('/')} className={getTabClass('/')} title="Dashboard">
            <Layout size={16} className={!isFullscreen ? "mr-2" : ""} /> {!isFullscreen && "DASHBOARD"}
          </button>
          <button onClick={() => navigate('/chart')} className={getTabClass('/chart')} title="Chart">
            <LineChart size={16} className={!isFullscreen ? "mr-2" : ""} /> {!isFullscreen && "CHART"}
          </button>
          <button onClick={() => navigate('/logs')} className={getTabClass('/logs')} title="Logs">
            <History size={16} className={!isFullscreen ? "mr-2" : ""} /> {!isFullscreen && "LOGS"}
          </button>
          <button onClick={() => navigate('/setting')} className={getTabClass('/setting')} title="Setting">
            <Settings size={16} className={!isFullscreen ? "mr-2" : ""} /> {!isFullscreen && "SETTING"}
          </button>
        </nav>

        <button 
          onClick={toggleOSFullscreen}
          className={`text-text-secondary hover:text-text-primary transition-colors flex items-center justify-center ${isFullscreen ? 'p-2 rounded-lg hover:bg-bg-surface' : 'p-2 bg-bg-surface border border-border rounded-lg'}`}
          title="Toggle Fullscreen"
        >
          {isTrueFullscreen ? <Minimize size={20} /> : <Maximize size={20} />}
        </button>

        <button 
          onClick={() => setIsDarkMode(!isDarkMode)}
          className={`text-text-secondary hover:text-text-primary transition-colors flex items-center justify-center ${isFullscreen ? 'p-2 rounded-lg hover:bg-bg-surface' : 'p-2 bg-bg-surface border border-border rounded-lg'}`}
          title="Toggle Theme"
        >
          {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>
        
        <div className="h-8 w-px bg-border"></div>
        
        {/* LOGIN INFORMATION */}
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
          </div>
          
          <button 
            onClick={handleLogout}
            className={`text-red-400 hover:text-red-300 transition-colors flex items-center justify-center ${isFullscreen ? 'p-2 rounded-lg hover:bg-red-500/10' : 'p-2 hover:bg-red-500/10 rounded-lg border border-transparent hover:border-red-500/30'}`}
            title="Logout"
          >
            <LogOut size={20} />
          </button>
        </div>
      </div>
    </header>
  );
}
