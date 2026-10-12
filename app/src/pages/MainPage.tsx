import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Activity, 
  ArrowRight, 
  LogOut, 
  Users, 
  UserPlus, 
  Shield, 
  Monitor, 
  RefreshCw, 
  CheckCircle2, 
  AlertCircle, 
  X,
  Radio,
  ExternalLink
} from 'lucide-react';
import { appPath, goToLogin } from '../routes';

interface OnlineSession {
  session_id: string;
  user_id: string;
  username: string;
  role: string;
  plan: string;
  ip_address: string | null;
  user_agent: string | null;
  last_seen: string;
  is_current: boolean;
}

interface AppUser {
  id: number;
  username: string;
  user_id: string;
  role: string;
  plan: string;
  created_at: string;
}

export default function MainPage() {
  const navigate = useNavigate();
  const userId = localStorage.getItem('userId') || '';
  const role = localStorage.getItem('userRole') || '';
  const plan = localStorage.getItem('userPlan') || 'trial';
  const token = localStorage.getItem('jwt_token') || '';

  // Session & Management states
  const [concurrentCount, setConcurrentCount] = useState<number>(1);
  const [onlineSessions, setOnlineSessions] = useState<OnlineSession[]>([]);
  const [userList, setUserList] = useState<AppUser[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [activeTab, setActiveTab] = useState<'presence' | 'users'>('presence');

  // Form states for adding user (Pro only)
  const [showAddUserModal, setShowAddUserModal] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newRole, setNewRole] = useState('OPERATOR');
  const [newPlan, setNewPlan] = useState('pro');
  const [formError, setFormError] = useState('');
  const [formSuccess, setFormSuccess] = useState('');
  const [submittingUser, setSubmittingUser] = useState(false);

  useEffect(() => {
    document.documentElement.className = 'dark';
  }, []);

  const logout = async () => {
    try {
      if (token) {
        await fetch('/api/v1/auth/logout', {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        });
      }
    } catch {
      // ignore
    }
    ['jwt_token', 'userId', 'userRole', 'userPlan'].forEach((k) => localStorage.removeItem(k));
    goToLogin(navigate);
  };

  // Heartbeat & session fetch
  const refreshSessions = useCallback(async () => {
    if (!token) return;
    try {
      // 1. Heartbeat ping
      fetch('/api/v1/auth/heartbeat', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      }).catch(() => {});

      // 2. Fetch session info
      const res = await fetch('/api/v1/auth/sessions/active', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const json = await res.json();
        if (json.success && json.data) {
          if (json.data.type === 'trial') {
            setConcurrentCount(json.data.concurrent_count || 1);
          } else if (json.data.type === 'pro') {
            setOnlineSessions(json.data.sessions || []);
          }
        }
      }
    } catch {
      // ignore network errors
    }
  }, [token]);

  const fetchUsers = useCallback(async () => {
    if (!token || plan !== 'pro') return;
    setLoadingUsers(true);
    try {
      const res = await fetch('/api/v1/users', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const json = await res.json();
        if (json.success && Array.isArray(json.data)) {
          setUserList(json.data);
        }
      }
    } catch {
      // ignore
    } finally {
      setLoadingUsers(false);
    }
  }, [token, plan]);

  useEffect(() => {
    refreshSessions();
    const interval = setInterval(refreshSessions, 30000);
    return () => clearInterval(interval);
  }, [refreshSessions]);

  useEffect(() => {
    if (showSettingsModal && plan === 'pro') {
      fetchUsers();
    }
  }, [showSettingsModal, plan, fetchUsers]);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');
    setFormSuccess('');
    setSubmittingUser(true);

    try {
      const res = await fetch('/api/v1/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          username: newUsername.trim(),
          password: newPassword,
          role: newRole,
          plan: newPlan,
        }),
      });

      const json = await res.json();
      if (!res.ok || !json.success) {
        setFormError(json.message || 'Failed to create user account.');
        return;
      }

      setFormSuccess(`User ${newUsername} created successfully!`);
      setNewUsername('');
      setNewPassword('');
      fetchUsers();
      setTimeout(() => {
        setShowAddUserModal(false);
        setFormSuccess('');
      }, 1500);
    } catch {
      setFormError('Network error while provisioning user.');
    } finally {
      setSubmittingUser(false);
    }
  };

  return (
    <div className="dark min-h-screen bg-[#0a0a0a] text-gray-200 font-sans relative overflow-hidden">
      {/* Glow backgrounds */}
      <div className="absolute inset-0 pointer-events-none opacity-20">
        <div className="absolute top-[15%] left-[10%] w-72 h-72 md:w-96 md:h-96 bg-cyan-600 rounded-full mix-blend-screen blur-[100px]" />
        <div className="absolute bottom-[15%] right-[10%] w-72 h-72 md:w-96 md:h-96 bg-blue-600 rounded-full mix-blend-screen blur-[100px]" />
      </div>

      {/* Top Header */}
      <header className="relative z-10 flex items-center justify-between px-4 md:px-8 h-16 border-b border-[#2a303c] bg-[#0a0c10]/80 backdrop-blur">
        <div className="flex items-center gap-3 pt-1">
          <img src="/sentry-logo-noname.jpg" alt="SENTRY" className="h-9 w-auto rounded-md" />
          <div className="flex flex-col">
            <span className="font-bold tracking-widest uppercase text-sm md:text-base leading-none">Sentry SCADA</span>
            <span className="text-[10px] text-gray-400 font-mono tracking-wider">KAG Industrial Automation</span>
          </div>
        </div>
        <div className="flex items-center gap-3 md:gap-4">
          <div className="text-right hidden sm:block">
            <div className="text-xs font-bold tracking-widest text-cyan-400">{role}</div>
            <div className="text-[10px] font-mono text-gray-400">ID: {userId}</div>
          </div>
          <button 
            onClick={logout} 
            title="Logout" 
            className="p-2 rounded-lg text-red-400 hover:bg-red-500/10 border border-transparent hover:border-red-500/30 transition-colors"
          >
            <LogOut size={20} />
          </button>
        </div>
      </header>

      {/* Main Workspace Launcher */}
      <main className="relative z-10 max-w-5xl mx-auto px-4 md:px-8 py-10 md:py-14">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-[#222734]">
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-2xl md:text-3xl font-bold tracking-wide">Application Console</h1>
              <span className={`text-[11px] font-extrabold uppercase px-2.5 py-0.5 rounded tracking-wider ${
                plan === 'trial' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40' : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
              }`}>
                {plan === 'trial' ? 'Trial Evaluation' : 'Enterprise Pro'}
              </span>
            </div>
            <p className="text-gray-400 mt-1.5 text-sm">Select an active monitoring station or configure platform settings.</p>
          </div>

          <div className="flex items-center gap-2 text-xs text-gray-400 bg-[#141822] px-3.5 py-2 rounded-xl border border-[#2a303c]">
            <Radio size={14} className="text-emerald-400 animate-pulse" />
            <span>Telemetry link: <strong className="text-emerald-400 font-mono">ONLINE</strong></span>
          </div>
        </div>

        {/* Dashboard Launcher Cards */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Card 1: Main Application (DTS BC4 BC5) */}
          <button
            onClick={() => navigate(appPath('/'))}
            className="group text-left bg-gradient-to-br from-[#121620] to-[#0e1118] border border-[#262c3a] hover:border-cyan-500/80 rounded-2xl p-6 transition-all duration-200 hover:shadow-[0_0_35px_rgba(6,182,212,0.18)] focus:outline-none"
          >
            <div className="flex items-start justify-between">
              <div className="h-13 w-13 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center border border-cyan-500/20 group-hover:scale-105 transition-transform">
                <Activity size={28} />
              </div>
              <span className="text-[10px] font-mono tracking-widest uppercase bg-cyan-950/60 text-cyan-300 border border-cyan-800/60 px-2.5 py-1 rounded-full">
                Active System
              </span>
            </div>
            <h2 className="mt-5 text-xl font-bold tracking-wide uppercase group-hover:text-cyan-300 transition-colors">
              DTS BC4 BC5
            </h2>
            <p className="mt-2 text-sm text-gray-400 leading-relaxed">
              Real-time distributed temperature sensing telemetry, conveyor thermal profiling, hot spot alarm monitoring, and spatial logs for BC4 &amp; BC5.
            </p>
            <div className="mt-6 flex items-center text-cyan-400 text-sm font-bold tracking-widest uppercase">
              Launch Application <ArrowRight size={16} className="ml-2 group-hover:translate-x-1.5 transition-transform" />
            </div>
          </button>

          {/* Card 2: Settings & User Management (Pro) or Device Limit Monitor (Trial) */}
          {plan === 'pro' ? (
            <button
              onClick={() => {
                setShowSettingsModal(true);
                setActiveTab('presence');
              }}
              className="group text-left bg-gradient-to-br from-[#121620] to-[#0e1118] border border-[#262c3a] hover:border-emerald-500/80 rounded-2xl p-6 transition-all duration-200 hover:shadow-[0_0_35px_rgba(16,185,129,0.18)] focus:outline-none"
            >
              <div className="flex items-start justify-between">
                <div className="h-13 w-13 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center border border-emerald-500/20 group-hover:scale-105 transition-transform">
                  <Users size={28} />
                </div>
                <span className="text-[10px] font-mono tracking-widest uppercase bg-emerald-950/60 text-emerald-300 border border-emerald-800/60 px-2.5 py-1 rounded-full">
                  {onlineSessions.length} Online Now
                </span>
              </div>
              <h2 className="mt-5 text-xl font-bold tracking-wide uppercase group-hover:text-emerald-300 transition-colors">
                Settings &amp; User Management
              </h2>
              <p className="mt-2 text-sm text-gray-400 leading-relaxed">
                Enterprise control panel: provision operator accounts, configure authorization roles, and audit real-time active user sessions.
              </p>
              <div className="mt-6 flex items-center text-emerald-400 text-sm font-bold tracking-widest uppercase">
                Open Management <ArrowRight size={16} className="ml-2 group-hover:translate-x-1.5 transition-transform" />
              </div>
            </button>
          ) : (
            <div className="text-left bg-gradient-to-br from-[#161412] to-[#110e0b] border border-amber-500/30 rounded-2xl p-6">
              <div className="flex items-start justify-between">
                <div className="h-13 w-13 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center border border-amber-500/20">
                  <Monitor size={28} />
                </div>
                <span className="text-[10px] font-mono tracking-widest uppercase bg-amber-950/80 text-amber-400 border border-amber-800/60 px-2.5 py-1 rounded-full font-bold">
                  Concurrent Devices: {concurrentCount} / 10
                </span>
              </div>
              <h2 className="mt-5 text-xl font-bold tracking-wide uppercase text-amber-300">
                Session &amp; Device Quota
              </h2>
              <p className="mt-2 text-sm text-gray-300 leading-relaxed">
                Trial accounts operate under shared credentials <span className="font-mono text-amber-400 font-bold">TCM-TRIAL</span>, capped at <strong>10 concurrent active devices</strong>.
              </p>

              {/* Progress bar */}
              <div className="mt-4">
                <div className="flex justify-between text-xs text-gray-400 mb-1.5">
                  <span>Capacity utilization</span>
                  <span className="font-mono font-bold text-amber-400">{concurrentCount} of 10 used</span>
                </div>
                <div className="w-full bg-[#201c18] rounded-full h-2.5 overflow-hidden border border-amber-900/30">
                  <div 
                    className="bg-amber-500 h-2.5 rounded-full transition-all duration-500" 
                    style={{ width: `${Math.min(100, (concurrentCount / 10) * 100)}%` }} 
                  />
                </div>
              </div>

              <div className="mt-5 pt-4 border-t border-amber-950 flex items-center justify-between">
                <span className="text-xs text-gray-400">User management is restricted in Trial</span>
                <a 
                  href="/#contact" 
                  className="text-xs text-amber-400 font-bold hover:underline inline-flex items-center gap-1"
                >
                  Upgrade to Pro <ExternalLink size={12} />
                </a>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Pro Settings & User Management Modal */}
      {showSettingsModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="bg-[#10141d] border border-[#2b3345] rounded-2xl w-full max-w-3xl overflow-hidden shadow-2xl flex flex-col max-h-[88vh]">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-[#222a3a] bg-[#0c1017]">
              <div className="flex items-center gap-3">
                <Shield className="text-emerald-400" size={22} />
                <div>
                  <h3 className="font-bold text-lg text-white">Platform Settings &amp; User Administration</h3>
                  <p className="text-xs text-gray-400">Enterprise Pro tier access</p>
                </div>
              </div>
              <button 
                onClick={() => setShowSettingsModal(false)}
                className="text-gray-400 hover:text-white p-1 rounded-lg hover:bg-white/5"
              >
                <X size={20} />
              </button>
            </div>

            {/* Navigation Tabs */}
            <div className="flex items-center px-6 border-b border-[#222a3a] bg-[#0e121a]">
              <button
                onClick={() => setActiveTab('presence')}
                className={`py-3 px-4 text-sm font-semibold tracking-wide border-b-2 transition-colors flex items-center gap-2 ${
                  activeTab === 'presence'
                    ? 'border-emerald-500 text-emerald-400'
                    : 'border-transparent text-gray-400 hover:text-gray-200'
                }`}
              >
                <Radio size={16} className={activeTab === 'presence' ? 'text-emerald-400' : ''} />
                Live Online Users ({onlineSessions.length})
              </button>
              <button
                onClick={() => setActiveTab('users')}
                className={`py-3 px-4 text-sm font-semibold tracking-wide border-b-2 transition-colors flex items-center gap-2 ${
                  activeTab === 'users'
                    ? 'border-emerald-500 text-emerald-400'
                    : 'border-transparent text-gray-400 hover:text-gray-200'
                }`}
              >
                <Users size={16} className={activeTab === 'users' ? 'text-emerald-400' : ''} />
                User Accounts Directory ({userList.length})
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto flex-1">
              {activeTab === 'presence' && (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <p className="text-xs text-gray-400">
                      Real-time presence of operator and administrator clients connected within the last 15 minutes.
                    </p>
                    <button 
                      onClick={refreshSessions}
                      className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-semibold"
                    >
                      <RefreshCw size={13} /> Refresh
                    </button>
                  </div>

                  {onlineSessions.length === 0 ? (
                    <div className="text-center py-8 text-gray-500 text-sm">
                      No active sessions found.
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {onlineSessions.map((s) => (
                        <div 
                          key={s.session_id}
                          className="bg-[#151a24] border border-[#232b3b] rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                        >
                          <div className="flex items-center gap-3">
                            <div className="relative">
                              <div className="w-10 h-10 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold text-sm">
                                {s.username.substring(0, 2).toUpperCase()}
                              </div>
                              <span className="absolute bottom-0 right-0 w-3 h-3 bg-emerald-500 border-2 border-[#151a24] rounded-full" />
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <span className="font-bold text-sm text-white">{s.username}</span>
                                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-gray-800 text-gray-300">
                                  {s.role}
                                </span>
                                {s.is_current && (
                                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
                                    Current Device
                                  </span>
                                )}
                              </div>
                              <div className="text-xs text-gray-400 font-mono mt-0.5">
                                User ID: {s.user_id} &bull; Plan: {s.plan.toUpperCase()}
                              </div>
                            </div>
                          </div>

                          <div className="text-right text-xs text-gray-400 font-mono">
                            <div>IP: {s.ip_address || 'Internal Network'}</div>
                            <div className="text-[11px] text-gray-500">
                              Active: {new Date(s.last_seen).toLocaleTimeString()}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'users' && (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <p className="text-xs text-gray-400">
                      Manage operator credentials, assign roles, and provision new team members.
                    </p>
                    <button
                      onClick={() => {
                        setShowAddUserModal(true);
                        setFormError('');
                        setFormSuccess('');
                      }}
                      className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold flex items-center gap-1.5 transition-colors"
                    >
                      <UserPlus size={14} /> Add New User
                    </button>
                  </div>

                  {loadingUsers ? (
                    <div className="text-center py-8 text-gray-400 text-sm">
                      Loading user accounts...
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs border-collapse">
                        <thead>
                          <tr className="border-b border-[#232b3b] text-gray-400 font-mono uppercase text-[10px]">
                            <th className="py-2.5 px-3">Username</th>
                            <th className="py-2.5 px-3">User ID</th>
                            <th className="py-2.5 px-3">Role</th>
                            <th className="py-2.5 px-3">Plan</th>
                            <th className="py-2.5 px-3">Created</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-[#1e2533]">
                          {userList.map((u) => (
                            <tr key={u.id} className="hover:bg-white/5 transition-colors">
                              <td className="py-3 px-3 font-semibold text-white">{u.username}</td>
                              <td className="py-3 px-3 font-mono text-gray-300">{u.user_id}</td>
                              <td className="py-3 px-3">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                  u.role === 'ADMINISTRATOR' 
                                    ? 'bg-purple-500/20 text-purple-300' 
                                    : 'bg-blue-500/20 text-blue-300'
                                }`}>
                                  {u.role}
                                </span>
                              </td>
                              <td className="py-3 px-3">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                  u.plan === 'pro' 
                                    ? 'bg-emerald-500/20 text-emerald-300' 
                                    : 'bg-amber-500/20 text-amber-300'
                                }`}>
                                  {u.plan.toUpperCase()}
                                </span>
                              </td>
                              <td className="py-3 px-3 text-gray-400 font-mono">
                                {new Date(u.created_at).toLocaleDateString()}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Add User Modal */}
      {showAddUserModal && (
        <div className="fixed inset-0 z-60 flex items-center justify-center bg-black/85 backdrop-blur-md p-4">
          <div className="bg-[#121622] border border-[#2b3548] rounded-2xl w-full max-w-md p-6 shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-[#232b3b]">
              <h4 className="font-bold text-white text-base flex items-center gap-2">
                <UserPlus size={18} className="text-emerald-400" /> Provision Operator Account
              </h4>
              <button 
                onClick={() => setShowAddUserModal(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={18} />
              </button>
            </div>

            {formError && (
              <div className="mt-4 p-3 rounded-lg bg-red-500/15 border border-red-500/30 text-red-400 text-xs flex items-center gap-2">
                <AlertCircle size={16} /> {formError}
              </div>
            )}

            {formSuccess && (
              <div className="mt-4 p-3 rounded-lg bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
                <CheckCircle2 size={16} /> {formSuccess}
              </div>
            )}

            <form onSubmit={handleCreateUser} className="mt-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">Username</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. operator_field_b"
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  className="w-full bg-[#181e2b] border border-[#2e374a] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">Password</label>
                <input
                  type="password"
                  required
                  placeholder="Enter initial password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full bg-[#181e2b] border border-[#2e374a] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1">Role</label>
                  <select
                    value={newRole}
                    onChange={(e) => setNewRole(e.target.value)}
                    className="w-full bg-[#181e2b] border border-[#2e374a] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="OPERATOR">OPERATOR</option>
                    <option value="VIEWER">VIEWER</option>
                    <option value="ADMINISTRATOR">ADMINISTRATOR</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1">Plan</label>
                  <select
                    value={newPlan}
                    onChange={(e) => setNewPlan(e.target.value)}
                    className="w-full bg-[#181e2b] border border-[#2e374a] rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                  >
                    <option value="pro">Enterprise Pro</option>
                    <option value="trial">Trial</option>
                  </select>
                </div>
              </div>

              <div className="pt-3 flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddUserModal(false)}
                  className="px-4 py-2 rounded-lg text-xs font-semibold text-gray-400 hover:bg-white/5"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingUser}
                  className="px-4 py-2 rounded-lg text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-50"
                >
                  {submittingUser ? 'Creating...' : 'Create Account'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
