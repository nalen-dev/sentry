import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ChartPage from './pages/ChartPage';
import LogsPage from './pages/LogsPage';
import SettingPage from './pages/SettingPage';
import { ToastProvider } from './contexts/ToastContext';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = localStorage.getItem('userRole') !== null;
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
}

function App() {
  return (
    <ToastProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/chart" element={
            <ProtectedRoute>
              <ChartPage />
            </ProtectedRoute>
          } />
          <Route path="/logs" element={
            <ProtectedRoute>
              <LogsPage />
            </ProtectedRoute>
          } />
          <Route path="/setting" element={
            <ProtectedRoute>
              <SettingPage />
            </ProtectedRoute>
          } />
          {/* Redirect any unknown routes to dashboard */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </ToastProvider>
  );
}

export default App;
