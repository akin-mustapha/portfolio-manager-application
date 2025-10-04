import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppProvider } from './contexts/AppContext';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import ApiSetup from './pages/ApiSetup';
import PieAnalysis from './pages/PieAnalysis';
import Settings from './pages/Settings';
import './App.css';

function App() {
  return (
    <AppProvider>
      <Router>
        <div className="App">
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/api-setup" element={<ApiSetup />} />
              <Route path="/pie-analysis" element={<PieAnalysis />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Layout>
        </div>
      </Router>
    </AppProvider>
  );
}

export default App;