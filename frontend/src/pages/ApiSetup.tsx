import React, { useState } from 'react';
import { useAppContext } from '../contexts/AppContext';
import { apiService } from '../services/api';
import { useMutation } from '@tanstack/react-query';

const ApiSetup: React.FC = () => {
  const { auth } = useAppContext();
  const [apiKey, setApiKey] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);

  const validateApiKeyMutation = useMutation({
    mutationFn: apiService.validateApiKey,
    onSuccess: (data) => {
      if (data.data.valid) {
        auth.setApiKey(apiKey);
        setErrors([]);
      } else {
        setErrors(['Invalid API key. Please check your credentials.']);
      }
    },
    onError: (error: any) => {
      setErrors([error.message || 'Failed to validate API key']);
      auth.setConnectionStatus('error');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrors([]);
    
    if (!apiKey.trim()) {
      setErrors(['API key is required']);
      return;
    }

    auth.setConnectionStatus('connecting');
    validateApiKeyMutation.mutate(apiKey.trim());
  };

  const handleDisconnect = () => {
    auth.clearAuth();
    setApiKey('');
    setErrors([]);
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
    switch (auth.connectionStatus) {
      case 'connected': return 'Connected to Trading 212';
      case 'connecting': return 'Connecting to Trading 212...';
      case 'error': return 'Connection failed';
      default: return 'Not connected';
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
            <div className={`w-3 h-3 rounded-full mr-3 ${
              auth.connectionStatus === 'connected' ? 'bg-green-500' :
              auth.connectionStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' :
              auth.connectionStatus === 'error' ? 'bg-red-500' :
              'bg-gray-400'
            }`} />
            <span className="font-medium">{getConnectionStatusText()}</span>
          </div>
          {auth.isAuthenticated && auth.authState.lastConnected && (
            <span className="text-sm">
              Last connected: {new Date(auth.authState.lastConnected).toLocaleString()}
            </span>
          )}
        </div>
      </div>

      {/* API Key Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          API Configuration
        </h3>
        
        {!auth.isAuthenticated ? (
          <form onSubmit={handleSubmit} className="space-y-4">
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
                  disabled={validateApiKeyMutation.isPending}
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
                You can find your API key in your Trading 212 account settings.
              </p>
            </div>

            {errors.length > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-md p-3">
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

            <button
              type="submit"
              disabled={validateApiKeyMutation.isPending || !apiKey.trim()}
              className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {validateApiKeyMutation.isPending ? 'Connecting...' : 'Connect to Trading 212'}
            </button>
          </form>
        ) : (
          <div className="space-y-4">
            <div className="bg-green-50 border border-green-200 rounded-md p-4">
              <div className="flex items-center">
                <div className="text-green-400 mr-2">✅</div>
                <div>
                  <h4 className="text-sm font-medium text-green-800">
                    Successfully Connected
                  </h4>
                  <p className="text-sm text-green-700">
                    Your Trading 212 API is connected and ready to use.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={handleDisconnect}
                className="bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
              >
                Disconnect
              </button>
              <button
                onClick={() => validateApiKeyMutation.mutate(auth.authState.apiKey!)}
                disabled={validateApiKeyMutation.isPending}
                className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
              >
                {validateApiKeyMutation.isPending ? 'Testing...' : 'Test Connection'}
              </button>
            </div>
          </div>
        )}
      </div>

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
            <strong>Security Note:</strong> Your API key is stored securely in your browser's local storage and is never sent to our servers. It's only used to communicate directly with Trading 212's API.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ApiSetup;