import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity } from 'lucide-react';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // For MVP, just redirect to dashboard
    navigate('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-scada-dark p-4">
      <div className="w-full max-w-md bg-scada-panel border border-scada-border rounded-lg shadow-xl overflow-hidden">
        <div className="p-6 text-center border-b border-scada-border bg-black/20">
          <Activity className="w-12 h-12 text-scada-primary mx-auto mb-2" />
          <h1 className="text-2xl font-bold text-white tracking-wider">DTS READER</h1>
          <p className="text-sm text-gray-400">Fiber Optic Monitoring System</p>
        </div>
        
        <form onSubmit={handleLogin} className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Username</label>
            <input 
              type="text" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-scada-dark border border-scada-border rounded px-4 py-2 text-white focus:outline-none focus:border-scada-primary focus:ring-1 focus:ring-scada-primary transition-colors"
              placeholder="admin"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Password</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-scada-dark border border-scada-border rounded px-4 py-2 text-white focus:outline-none focus:border-scada-primary focus:ring-1 focus:ring-scada-primary transition-colors"
              placeholder="••••••••"
            />
          </div>

          <button 
            type="submit"
            className="w-full bg-scada-primary hover:bg-opacity-90 text-white font-semibold py-2 px-4 rounded transition-colors"
          >
            LOGIN
          </button>
        </form>
      </div>
    </div>
  );
}
