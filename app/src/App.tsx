import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ChartPage from './pages/ChartPage';
import LogsPage from './pages/LogsPage';
import SettingPage from './pages/SettingPage';
import MainPage from './pages/MainPage';
import TrialRibbon from './components/TrialRibbon';
import { ToastProvider } from './contexts/ToastContext';
import { isWebTarget } from './data';
import { APP_BASE, MAIN_PATH, appPath, goToLogin } from './routes';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = isWebTarget
    ? localStorage.getItem('jwt_token') !== null
    : localStorage.getItem('userRole') !== null;

  if (!isAuthenticated) {
    if (isWebTarget) {
      // Web: login page is owned by the static site at /login
      goToLogin();
      return null;
    }
    return <Navigate to="/login" replace />;
  }

  return children;
}

function App() {
  const protect = (el: React.ReactNode) => <ProtectedRoute>{el}</ProtectedRoute>;

  return (
    <ToastProvider>
      <Router>
        <TrialRibbon />
        <Routes>
          {/* Desktop keeps its local login; on web /login is served by the static site (Caddy),
              this route is only a dev fallback. */}
          <Route path="/login" element={<Login />} />

          {isWebTarget && (
            <>
              <Route path={MAIN_PATH} element={protect(<MainPage />)} />
              <Route path="/menu" element={protect(<MainPage />)} />
            </>
          )}

          <Route path={appPath('/')} element={protect(<Dashboard />)} />
          <Route path={appPath('/chart')} element={protect(<ChartPage />)} />
          <Route path={appPath('/logs')} element={protect(<LogsPage />)} />
          <Route path={appPath('/setting')} element={protect(<SettingPage />)} />

          {/* Unknown routes: web -> launcher, desktop -> dashboard */}
          <Route
            path="*"
            element={<Navigate to={isWebTarget ? (APP_BASE ? MAIN_PATH : '/') : '/'} replace />}
          />
        </Routes>
      </Router>
    </ToastProvider>
  );
}

export default App;
