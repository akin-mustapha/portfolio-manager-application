import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppProvider } from './contexts/AppContext';
import { useAuthError } from './hooks/useAuthError';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';

import PieAnalysis from './pages/PieAnalysis';
import PerformanceAnalysis from './pages/PerformanceAnalysis';
import Settings from './pages/Settings';

import './App.css';

function AppContent() {
  useAuthError();

  return (
    <Routes>
      <Route path="/" element={
        <Layout>
          <Dashboard />
        </Layout>
      } />
      <Route path="/dashboard" element={
        <Layout>
          <Dashboard />
        </Layout>
      } />

      <Route path="/pie-analysis" element={
        <Layout>
          <PieAnalysis />
        </Layout>
      } />
      <Route path="/performance" element={
        <Layout>
          <PerformanceAnalysis />
        </Layout>
      } />
      <Route path="/settings" element={
        <Layout>
          <Settings />
        </Layout>
      } />

    </Routes>
  );
}

function App() {
  return (
    <AppProvider>
      <Router>
        <div className="App">
          <AppContent />
        </div>
      </Router>
    </AppProvider>
  );
}

export default App;