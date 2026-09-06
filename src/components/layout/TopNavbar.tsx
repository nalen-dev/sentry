import { Sun, Moon, Layout, History, LineChart, Settings, User, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface TopNavbarProps {
  isFullscreen: boolean;
  setIsFullscreen: (val: boolean) => void;
  isDarkMode: boolean;
  setIsDarkMode: (val: boolean) => void;
  userRole: string;
  userId: string;
}

export default function TopNavbar({ 
  isFullscreen,
  isDarkMode, 
  setIsDarkMode, 
  userRole, 
  userId 
}: TopNavbarProps) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('userRole');
    localStorage.removeItem('userId');
    navigate('/login');
  };

  return (
    <header className={`z-30 transition-all duration-500 flex items-center shadow-md border-border ${
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
          <button className={`text-scada-primary font-bold transition-colors flex items-center tracking-widest ${isFullscreen ? 'p-2 rounded-lg bg-scada-primary/10' : 'text-sm'}`} title="Dashboard">
            <Layout size={16} className={!isFullscreen ? "mr-2" : ""} /> {!isFullscreen && "DASHBOARD"}
          </button>
          <button className={`text-text-secondary hover:text-text-primary font-bold transition-colors flex items-center tracking-widest ${isFullscreen ? 'p-2 rounded-lg hover:bg-bg-surface' : 'text-sm'}`} title="Logs">
            <History size={16} className={!isFullscreen ? "mr-2" : ""} /> {!isFullscreen && "LOGS"}
          </button>
          <button className={`text-text-secondary hover:text-text-primary font-bold transition-colors flex items-center tracking-widest ${isFullscreen ? 'p-2 rounded-lg hover:bg-bg-surface' : 'text-sm'}`} title="Chart">
            <LineChart size={16} className={!isFullscreen ? "mr-2" : ""} /> {!isFullscreen && "CHART"}
          </button>
          <button className={`text-text-secondary hover:text-text-primary font-bold transition-colors flex items-center tracking-widest ${isFullscreen ? 'p-2 rounded-lg hover:bg-bg-surface' : 'text-sm'}`} title="Setting">
            <Settings size={16} className={!isFullscreen ? "mr-2" : ""} /> {!isFullscreen && "SETTING"}
          </button>
        </nav>

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
