import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, User, ShieldCheck, AlertCircle } from 'lucide-react';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(false);
  const navigate = useNavigate();

  // Force dark mode context for this page
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  const handleLogin = (e: React.FormEvent) => {
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
  };

  return (
    <div className="dark min-h-screen flex items-center justify-center bg-[#0a0a0a] p-4 relative overflow-hidden font-sans">
      
      {/* Decorative Background Elements */}
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none opacity-20">
        <div className="absolute top-[20%] left-[10%] w-96 h-96 bg-cyan-600 rounded-full mix-blend-screen filter blur-[100px] animate-pulse"></div>
        <div className="absolute bottom-[20%] right-[10%] w-96 h-96 bg-blue-600 rounded-full mix-blend-screen filter blur-[100px] animate-pulse" style={{ animationDelay: '2s' }}></div>
      </div>
      
      {/* Grid Pattern */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjEiIGZpbGw9IiMzMzMiLz48L3N2Zz4=')] opacity-30"></div>

      <div className="relative z-10 w-full max-w-md bg-[#11141a]/90 backdrop-blur-xl border border-[#2a303c] rounded-2xl shadow-2xl overflow-hidden p-8">
        
        <div className="text-center mb-10 flex flex-col items-center">
          <img src="/sentry-logo.jpg" alt="SENTRY Logo" className="w-auto h-24 mb-4 object-contain rounded-xl shadow-[0_0_20px_rgba(6,182,212,0.2)]" />
          <p className="text-sm text-gray-400 mt-2 font-mono tracking-wide">INTEGRATED SCADA PLATFORM</p>
        </div>
        
        {error && (
          <div className="mb-6 p-3 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center text-red-400 text-sm">
            <AlertCircle size={16} className="mr-2 shrink-0" />
            <span>Invalid credentials. Try <b>admin</b> or <b>operator</b>.</span>
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-5">
          <div className="space-y-1">
            <label className="text-xs font-bold text-gray-400 uppercase tracking-widest pl-1">Username</label>
            <div className="relative">
              <User size={18} className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500" />
              <input 
                type="text" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-[#0a0a0a] border border-[#2a303c] rounded-xl pl-11 pr-4 py-3.5 text-gray-200 focus:outline-none focus:border-[#06b6d4] focus:ring-1 focus:ring-[#06b6d4] transition-all shadow-inner"
                placeholder="Enter username"
                required
              />
            </div>
          </div>
          
          <div className="space-y-1">
            <label className="text-xs font-bold text-gray-400 uppercase tracking-widest pl-1">Password</label>
            <div className="relative">
              <Lock size={18} className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500" />
              <input 
                type="password" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-[#0a0a0a] border border-[#2a303c] rounded-xl pl-11 pr-4 py-3.5 text-gray-200 focus:outline-none focus:border-[#06b6d4] focus:ring-1 focus:ring-[#06b6d4] transition-all shadow-inner"
                placeholder="••••••••"
                required
              />
            </div>
          </div>

          <div className="pt-4">
            <button 
              type="submit"
              className="w-full bg-[#06b6d4] hover:bg-[#0891b2] text-white font-bold tracking-widest uppercase py-3.5 px-4 rounded-xl transition-all shadow-[0_0_15px_rgba(6,182,212,0.4)] flex items-center justify-center"
            >
              <ShieldCheck size={20} className="mr-2" />
              Authenticate
            </button>
          </div>
        </form>

        <div className="mt-8 pt-6 border-t border-[#2a303c] text-center">
          <p className="text-[10px] text-gray-500 font-mono">
            SECURE CONNECTION • SYSTEM V2.4.1
          </p>
        </div>
      </div>
    </div>
  );
}
