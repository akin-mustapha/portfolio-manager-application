import React, { useState, useEffect } from 'react';
import { useAppContext } from '../contexts/AppContext';
import { useMutation } from '@tanstack/react-query';

const ApiSetup: React.FC = () => {
  const { auth } = useAppContext();
  const [apiKey, setApiKey] = useState('');
  const [sessionName, setSessionName] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [validationStep, setValidationStep] = useState<'session' | 'api' | 'complete'>('session');

  // Initialize session on component mount if not authenticated
  useEffect(() => {
    if (!auth.isAuthenticated) {
      setValidationStep('session');
    } else if (!auth.hasTrading212Connection) {
      setValidationStep('api');
    } else {
      setValidationStep('complete');
    }
  }, [auth.isAuthenticated, auth.hasTrading212Connection]);

  // Session creation mutation
  const createSessionMutation = useMutation({
    mutationFn: () => auth.initializeSession(sessionName || 'Portfolio Dashboard Session'),
    onSuccess: () => {
      setErrors([]);
      setValidationStep('api');
    },
    onError: (error: any) => {
      setErrors([error.message || 'Failed to create session']);
    },
  });

  // API key setup mutation
  const setupApiKeyMutation = useMutation({
    mutationFn: (apiKey: string) => auth.setupTrading212API(apiKey, true),
    onSuccess: (data) => {
      setErrors([]);
      setValidationStep('complete');
      setApiKey(''); // Clear the input for security
    },
    onError: (error: any) => {
      setErrors([error.message || 'Failed to setup Trading 212 API']);
      auth.setConnectionStatus('error');
    },
  });

  // API validation mutation (for testing existing connection)
  const validateApiMutation = useMutation({
    mutationFn: (apiKey: string) => auth.validateTrading212API(apiKey),
    onSuccess: (data) => {
      if (data.isValid) {
        setErrors([]);
      } else {
        setErrors([data.errorMessage || 'Invalid API key']);
      }
    },
    onError: (error: any) => {
      setErrors([error.message || 'Failed to validate API key']);
    },
  });

  // Disconnect mutation
  const disconnectMutation = useMutation({
    mutationFn: () => auth.disconnectTrading212(),
    onSuccess: () => {
      setErrors([]);
      setValidationStep('api');
    },
    onError: (error: any) => {
      setErrors([error.message || 'Failed to disconnect']);
    },
  });

  const handleSessionSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrors([]);
    createSessionMutation.mutate();
  };

  const handleApiSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrors([]);
    
    if (!apiKey.trim()) {
      setErrors(['API key is required']);
      return;
    }

    auth.setConnectionStatus('connecting');
    setupApiKeyMutation.mutate(apiKey.trim());
  };

  const handleTestConnection = () => {
    if (!auth.authState.apiKey) {
      setErrors(['No API key found']);
      return;
    }
    
    setErrors([]);
    validateApiMutation.mutate(auth.authState.apiKey);
  };

  const handleDisconnect = () => {
    setErrors([]);
    disconnectMutation.mutate();
  };

  const handleFullReset = async () => {
    setErrors([]);
    try {
      await auth.clearAuth();
      setValidationStep('session');
      setSessionName('');
      setApiKey('');
    } catch (error: any) {
      setErrors([error.message || 'Failed to reset session']);
    }
  };

  const getConnectionStatusColor = () => {
    switch (auth.connectionStatus) {
      case 'connected': return 'text-green-600 bg-green-50 border-green-200';
      case 'connecting': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'error': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getConnectionStatusText = () => {
    if (!auth.isAuthenticated) return 'No session';
    if (!auth.hasTrading212Connection) return 'Session active, Trading 212 not connected';
    
    switch (auth.connectionStatus) {
      case 'connected': return 'Connected to Trading 212';
      case 'connecting': return 'Connecting to Trading 212...';
      case 'error': return 'Trading 212 connection failed';
      default: return 'Session active';
    }
  };

  const getStatusIcon = () => {
    if (!auth.isAuthenticated) return 'bg-gray-400';
    if (!auth.hasTrading212Connection) return 'bg-yellow-500';
    
    switch (auth.connectionStatus) {
      case 'connected': return 'bg-green-500';
      case 'connecting': return 'bg-yellow-500 animate-pulse';
      case 'error': return 'bg-red-500';
      default: return 'bg-yellow-500';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Trading 212 API Setup
        </h2>
        <p className="text-gray-600">
          Connect your Trading 212 account to access your portfolio data and analytics.
        </p>
      </div>

      {/* Connection Status */}
      <div className={`rounded-lg border p-4 ${getConnectionStatusColor()}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className={`w-3 h-3 rounded-full mr-3 ${getStatusIcon()}`} />
            <span className="font-medium">{getConnectionStatusText()}</span>
          </div>
          <div className="text-sm space-y-1">
            {auth.authState.sessionId && (
              <div>Session: {auth.authState.sessionName || 'Active'}</div>
            )}
            {auth.authState.lastConnected && (
              <div>Last connected: {new Date(auth.authState.lastConnected).toLocaleString()}</div>
            )}
            {auth.authState.accountInfo && (
              <div>Account: {auth.authState.accountInfo.accountType} ({auth.authState.accountInfo.accountId})</div>
            )}
          </div>
        </div>
      </div>

      {/* Error Display */}
      {errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="text-red-400 mr-2">⚠️</div>
            <div>
              <h4 className="text-sm font-medium text-red-800">
                {errors.length === 1 ? 'Error' : 'Errors'}
              </h4>
              <ul className="mt-1 text-sm text-red-700">
                {errors.map((error, index) => (
                  <li key={index}>{error}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Step 1: Session Creation */}
      {validationStep === 'session' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Step 1: Create Session
          </h3>
          <p className="text-gray-600 mb-4">
            First, we'll create a secure session to manage your authentication.
          </p>
          
          <form onSubmit={handleSessionSubmit} className="space-y-4">
            <div>
              <label htmlFor="sessionName" className="block text-sm font-medium text-gray-700 mb-2">
                Session Name (Optional)
              </label>
              <input
                type="text"
                id="sessionName"
                value={sessionName}
                onChange={(e) => setSessionName(e.target.value)}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., My Portfolio Dashboard"
                disabled={createSessionMutation.isPending}
              />
              <p className="mt-1 text-sm text-gray-500">
                Give your session a name to help identify it later.
              </p>
            </div>

            <button
              type="submit"
              disabled={createSessionMutation.isPending}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {createSessionMutation.isPending ? 'Creating Session...' : 'Create Session'}
            </button>
          </form>
        </div>
      )}

      {/* Step 2: API Key Setup */}
      {validationStep === 'api' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Step 2: Trading 212 API Configuration
          </h3>
          <p className="text-gray-600 mb-4">
            Now connect your Trading 212 account by providing your API key.
          </p>
          
          <form onSubmit={handleApiSubmit} className="space-y-4">
            <div>
              <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-2">
                Trading 212 API Key
              </label>
              <div className="relative">
                <input
                  type={showApiKey ? 'text' : 'password'}
                  id="apiKey"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter your Trading 212 API key"
                  disabled={setupApiKeyMutation.isPending}
                />
                <button
                  type="button"
                  onClick={() => setShowApiKey(!showApiKey)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                >
                  {showApiKey ? '🙈' : '👁️'}
                </button>
              </div>
              <p className="mt-1 text-sm text-gray-500">
                Your API key will be validated and securely stored.
              </p>
            </div>

            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={setupApiKeyMutation.isPending || !apiKey.trim()}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {setupApiKeyMutation.isPending ? 'Connecting...' : 'Connect to Trading 212'}
              </button>
              <button
                type="button"
                onClick={handleFullReset}
                className="bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
              >
                Reset Session
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Step 3: Complete */}
      {validationStep === 'complete' && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Connection Complete
          </h3>
          
          <div className="bg-green-50 border border-green-200 rounded-md p-4 mb-4">
            <div className="flex items-center">
              <div className="text-green-400 mr-2">✅</div>
              <div>
                <h4 className="text-sm font-medium text-green-800">
                  Successfully Connected
                </h4>
                <p className="text-sm text-green-700">
                  Your Trading 212 API is connected and ready to use. You can now access your portfolio data.
                </p>
              </div>
            </div>
          </div>

          {auth.authState.accountInfo && (
            <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-4">
              <h4 className="text-sm font-medium text-blue-800 mb-2">Account Information</h4>
              <div className="text-sm text-blue-700 space-y-1">
                <div>Account ID: {auth.authState.accountInfo.accountId}</div>
                <div>Account Type: {auth.authState.accountInfo.accountType}</div>
              </div>
            </div>
          )}

          <div className="flex space-x-3">
            <button
              onClick={handleTestConnection}
              disabled={validateApiMutation.isPending}
              className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            >
              {validateApiMutation.isPending ? 'Testing...' : 'Test Connection'}
            </button>
            <button
              onClick={handleDisconnect}
              disabled={disconnectMutation.isPending}
              className="bg-yellow-600 text-white py-2 px-4 rounded-md hover:bg-yellow-700 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2 disabled:opacity-50"
            >
              {disconnectMutation.isPending ? 'Disconnecting...' : 'Disconnect Trading 212'}
            </button>
            <button
              onClick={handleFullReset}
              className="bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            >
              Reset All
            </button>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-3">
          How to get your Trading 212 API Key
        </h3>
        <ol className="list-decimal list-inside space-y-2 text-sm text-blue-800">
          <li>Log in to your Trading 212 account</li>
          <li>Go to Settings → API Settings</li>
          <li>Generate a new API key or copy your existing one</li>
          <li>Paste the API key in the field above</li>
          <li>Click "Connect to Trading 212" to establish the connection</li>
        </ol>
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
          <p className="text-sm text-yellow-800">
            <strong>Security Note:</strong> Your API key is encrypted and stored securely. 
            JWT tokens are used for session management with automatic refresh. 
            All communication with Trading 212 is done securely through our backend.
          </p>
        </div>
      </div>

      {/* Token Information (for debugging in development) */}
      {process.env.NODE_ENV === 'development' && auth.isAuthenticated && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-800 mb-2">Debug Information</h4>
          <div className="text-xs text-gray-600 space-y-1">
            <div>Session ID: {auth.authState.sessionId}</div>
            <div>Token Expires: {auth.authState.tokenExpiresAt?.toLocaleString()}</div>
            <div>Token Expired: {auth.isTokenExpired() ? 'Yes' : 'No'}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiSetup;