import React, { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useAppContext } from '../contexts/AppContext';
import { apiService } from '../services/api';
import { Icon } from './icons';

const AuthTest: React.FC = () => {
  const { auth } = useAppContext();
  const queryClient = useQueryClient();
  const [testResults, setTestResults] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const addResult = (message: string) => {
    setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const runFullTest = async () => {
    setIsLoading(true);
    setTestResults([]);
    
    try {
      // Step 1: Create session
      addResult('Creating session...');
      await auth.initializeSession('Test Session');
      addResult('[✓] Session created successfully');
      
      // Step 2: Setup API key
      addResult('Setting up Trading 212 API...');
      await auth.setupTrading212API('demo-api-key-12345', false);
      addResult('[✓] Trading 212 API setup successfully');
      
      // Step 3: Test portfolio endpoint
      addResult('Fetching portfolio data...');
      const portfolioData = await apiService.getPortfolio();
      addResult(`✅ Portfolio data: ${JSON.stringify(portfolioData)}`);
      
      // Step 4: Test pies endpoint
      addResult('Fetching pies data...');
      const piesData = await apiService.getPies();
      addResult(`✅ Pies data: ${JSON.stringify(piesData)}`);
      
    } catch (error: any) {
      addResult(`❌ Error: ${error.message}`);
      console.error('Test failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const runQuickSetup = async () => {
    try {
      addResult('Running quick setup...');
      if (!auth.isAuthenticated) {
        await auth.initializeSession('Quick Setup Session');
        addResult('✅ Session created');
      }
      if (!auth.hasTrading212Connection) {
        await auth.setupTrading212API('demo-api-key-12345', false);
        addResult('✅ API key configured');
      }
      addResult('✅ Setup complete - refresh page to see data');
    } catch (error: any) {
      addResult(`❌ Setup failed: ${error.message}`);
    }
  };

  const testHealthCheck = async () => {
    try {
      addResult('Testing health check...');
      const health = await apiService.healthCheck();
      addResult(`✅ Health check: ${JSON.stringify(health)}`);
    } catch (error: any) {
      addResult(`❌ Health check failed: ${error.message}`);
    }
  };

  const clearResults = () => {
    setTestResults([]);
  };

  const fetchPortfolioData = async () => {
    try {
      addResult('Manually fetching portfolio data...');
      
      // Manually fetch and cache the data
      const portfolioData = await queryClient.fetchQuery({
        queryKey: ['portfolio'],
        queryFn: apiService.getPortfolio,
      });
      
      const piesData = await queryClient.fetchQuery({
        queryKey: ['pies'],
        queryFn: apiService.getPies,
      });
      
      addResult(`✅ Portfolio fetched: £${portfolioData.totalValue?.toLocaleString()}`);
      addResult(`✅ Pies fetched: ${piesData.length} pies`);
      addResult('✅ Data loaded - refresh page to see dashboard');
      
    } catch (error: any) {
      addResult(`❌ Failed to fetch data: ${error.message}`);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">
        Authentication Test
      </h3>
      
      {/* Current Auth State */}
      <div className="bg-gray-50 border border-gray-200 rounded-md p-3 mb-4">
        <h4 className="text-sm font-medium text-gray-800 mb-2">Current Auth State</h4>
        <div className="text-xs text-gray-600 space-y-1">
          <div>Authenticated: {auth.isAuthenticated ? 'Yes' : 'No'}</div>
          <div>Has Trading 212: {auth.hasTrading212Connection ? 'Yes' : 'No'}</div>
          <div>Connection Status: {auth.connectionStatus}</div>
          <div>Session ID: {auth.authState.sessionId || 'None'}</div>
          <div>API Key: {auth.authState.apiKey ? 'Set' : 'Not set'}</div>
        </div>
      </div>

      {/* Test Buttons */}
      <div className="flex flex-wrap gap-2 mb-4">
        <button
          onClick={runQuickSetup}
          className="bg-green-600 text-white px-3 py-2 rounded-md hover:bg-green-700 text-sm"
        >
          Quick Setup
        </button>
        <button
          onClick={fetchPortfolioData}
          disabled={!auth.isAuthenticated || !auth.hasTrading212Connection}
          className="bg-indigo-600 text-white px-3 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50 text-sm"
        >
          Fetch Data
        </button>
        <button
          onClick={runFullTest}
          disabled={isLoading}
          className="bg-blue-600 text-white px-3 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 text-sm"
        >
          {isLoading ? 'Running...' : 'Full Test'}
        </button>
        <button
          onClick={testHealthCheck}
          className="bg-purple-600 text-white px-3 py-2 rounded-md hover:bg-purple-700 text-sm"
        >
          Health Check
        </button>
        <button
          onClick={clearResults}
          className="bg-gray-600 text-white px-3 py-2 rounded-md hover:bg-gray-700 text-sm"
        >
          Clear
        </button>
        <button
          onClick={() => window.location.reload()}
          className="bg-orange-600 text-white px-3 py-2 rounded-md hover:bg-orange-700 text-sm"
        >
          Refresh Page
        </button>
      </div>

      {/* Test Results */}
      {testResults.length > 0 && (
        <div className="bg-gray-50 border border-gray-200 rounded-md p-3">
          <h4 className="text-sm font-medium text-gray-800 mb-2">Test Results</h4>
          <div className="text-xs text-gray-600 space-y-1 max-h-60 overflow-y-auto">
            {testResults.map((result, index) => (
              <div key={index} className="font-mono">
                {result}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AuthTest;