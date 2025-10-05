import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppProvider } from './contexts/AppContext';
import { useAuthError } from './hooks/useAuthError';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import ApiSetup from './pages/ApiSetup';
import PieAnalysis from './pages/PieAnalysis';
import Settings from './pages/Settings';
import AnimationDemo from './components/AnimationDemo';
import PortfolioOverview from './components/PortfolioOverview';
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
      <Route path="/portfolio" element={<PortfolioOverview />} />
      <Route path="/api-setup" element={
        <Layout>
          <ApiSetup />
        </Layout>
      } />
      <Route path="/pie-analysis" element={
        <Layout>
          <PieAnalysis />
        </Layout>
      } />
      <Route path="/settings" element={
        <Layout>
          <Settings />
        </Layout>
      } />
      <Route path="/animation-demo" element={<AnimationDemo />} />
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