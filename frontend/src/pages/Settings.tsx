import React, { useState, useEffect } from 'react';
import { useAppContext } from '../contexts/AppContext';
import { useMutation } from '@tanstack/react-query';
import { Icon } from '../components/icons';
import ResponsiveContainer from '../components/ResponsiveContainer';
import DashboardGrid from '../components/DashboardGrid';
import { 
  Button, 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle,
  Input,
  Label,
  BorderBeam
} from '../components/ui';

const Settings: React.FC = () => {
  const { auth } = useAppContext();
  const [apiKey, setApiKey] = useState('');
  const [sessionName, setSessionName] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [activeTab, setActiveTab] = useState<'api' | 'preferences' | 'about'>('api');

  // Check connection status
  useEffect(() => {
    setIsConnected(auth.isAuthenticated && auth.hasTrading212Connection);
  }, [auth.isAuthenticated, auth.hasTrading212Connection]);

  // Combined setup mutation
  const setupMutation = useMutation({
    mutationFn: async ({ sessionName, apiKey }: { sessionName: string; apiKey: string }) => {
      // First create session if not authenticated
      if (!auth.isAuthenticated) {
        await auth.initializeSession(sessionName || 'Portfolio Dashboard Session');
      }
      // Then setup API key
      await auth.setupTrading212API(apiKey, true);
    },
    onSuccess: () => {
      setErrors([]);
      setIsConnected(true);
      setApiKey(''); // Clear the input for security
    },
    onError: (error: any) => {
      setErrors([error.message || 'Failed to setup connection']);
      auth.setConnectionStatus('error');
    },
  });

  // Disconnect mutation
  const disconnectMutation = useMutation({
    mutationFn: () => auth.clearAuth(),
    onSuccess: () => {
      setErrors([]);
      setIsConnected(false);
      setApiKey('');
      setSessionName('');
    },
    onError: (error: any) => {
      setErrors([error.message || 'Failed to disconnect']);
    },
  });

  const validateInputs = (): string[] => {
    const errors: string[] = [];
    
    if (!sessionName.trim() && !auth.isAuthenticated) {
      errors.push('Session name is required');
    }
    
    if (!apiKey.trim()) {
      errors.push('API key is required');
    } else {
      // Basic format validation for Trading 212 API keys
      if (apiKey.length < 10) {
        errors.push('API key appears to be too short');
      }
      
      if (!/^[A-Za-z0-9+/=_-]+$/.test(apiKey)) {
        errors.push('API key contains invalid characters');
      }
    }
    
    return errors;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrors([]);
    
    const validationErrors = validateInputs();
    if (validationErrors.length > 0) {
      setErrors(validationErrors);
      return;
    }

    auth.setConnectionStatus('connecting');
    setupMutation.mutate({
      sessionName: sessionName.trim(),
      apiKey: apiKey.trim()
    });
  };

  const handleDisconnect = () => {
    setErrors([]);
    disconnectMutation.mutate();
  };

  const getConnectionStatus = () => {
    if (isConnected) {
      return {
        text: 'Connected to Trading 212',
        color: 'text-success-600 dark:text-success-400',
        icon: <Icon name="CheckCircle" size="sm" className="text-success-500" />
      };
    } else if (setupMutation.isPending) {
      return {
        text: 'Connecting...',
        color: 'text-yellow-600 dark:text-yellow-400',
        icon: <Icon name="Refresh" size="sm" animation="spin" className="text-yellow-500" />
      };
    } else {
      return {
        text: 'Not Connected',
        color: 'text-gray-600 dark:text-gray-400',
        icon: <Icon name="AlertCircle" size="sm" className="text-gray-500" />
      };
    }
  };

  const tabs = [
    { id: 'api' as const, label: 'API Connection', icon: 'Wifi' },
    { id: 'preferences' as const, label: 'Preferences', icon: 'Settings' },
    { id: 'about' as const, label: 'About', icon: 'Info' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <ResponsiveContainer 
        variant="section" 
        animationStyle="from-top" 
        gradient={true}
      >
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Settings
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Manage your application settings and preferences
            </p>
          </div>
          <div className="flex items-center space-x-3">
            {getConnectionStatus().icon}
            <span className={`text-sm font-medium ${getConnectionStatus().color}`}>
              {getConnectionStatus().text}
            </span>
          </div>
        </div>
      </ResponsiveContainer>

      {/* Tab Navigation */}
      <ResponsiveContainer variant="section" animationStyle="from-left" animationDelay={0.1}>
        <div className="flex space-x-1 bg-gray-100/50 dark:bg-gray-800/50 p-1 rounded-lg">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                activeTab === tab.id
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100'
              }`}
            >
              <Icon name={tab.icon as any} size="sm" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </ResponsiveContainer>

      {/* Tab Content */}
      {activeTab === 'api' && (
        <div className="space-y-6">
          {/* Error Display */}
          {errors.length > 0 && (
            <ResponsiveContainer variant="card" animationStyle="from-top">
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <div className="flex">
                  <Icon name="AlertTriangle" size="sm" className="text-red-400 mr-2 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-medium text-red-800 dark:text-red-200">
                      {errors.length === 1 ? 'Error' : 'Errors'}
                    </h4>
                    <ul className="mt-1 text-sm text-red-700 dark:text-red-300">
                      {errors.map((error, index) => (
                        <li key={index}>• {error}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </ResponsiveContainer>
          )}

          {/* API Connection Card */}
          <ResponsiveContainer variant="card" animationStyle="from-bottom" animationDelay={0.2}>
            {!isConnected ? (
              <Card className="relative w-full overflow-hidden">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Icon name="Wifi" size="lg" className="mr-2 text-blue-600" />
                    Connect Trading 212 API
                  </CardTitle>
                  <CardDescription>
                    Enter your session name and API key to access your portfolio data.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit}>
                    <div className="grid w-full items-center gap-4">
                      {!auth.isAuthenticated && (
                        <div className="flex flex-col space-y-1.5">
                          <Label htmlFor="sessionName">Session Name</Label>
                          <Input
                            id="sessionName"
                            type="text"
                            placeholder="My Portfolio Dashboard"
                            value={sessionName}
                            onChange={(e) => setSessionName(e.target.value)}
                            disabled={setupMutation.isPending}
                          />
                        </div>
                      )}
                      <div className="flex flex-col space-y-1.5">
                        <Label htmlFor="apiKey">Trading 212 API Key</Label>
                        <div className="relative">
                          <Input
                            id="apiKey"
                            type={showApiKey ? 'text' : 'password'}
                            placeholder="Enter your API key"
                            value={apiKey}
                            onChange={(e) => {
                              setApiKey(e.target.value);
                              if (errors.length > 0) setErrors([]);
                            }}
                            disabled={setupMutation.isPending}
                            className="pr-10"
                          />
                          <button
                            type="button"
                            onClick={() => setShowApiKey(!showApiKey)}
                            className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 hover:text-gray-600"
                          >
                            <Icon name={showApiKey ? 'EyeOff' : 'Eye'} size="sm" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </form>
                </CardContent>
                <CardFooter className="flex justify-between">
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setSessionName('');
                      setApiKey('');
                      setErrors([]);
                    }}
                    disabled={setupMutation.isPending}
                  >
                    Clear
                  </Button>
                  <Button 
                    onClick={handleSubmit}
                    disabled={setupMutation.isPending || !apiKey.trim() || (!sessionName.trim() && !auth.isAuthenticated)}
                  >
                    {setupMutation.isPending ? (
                      <>
                        <Icon name="Refresh" size="sm" animation="spin" className="mr-2" />
                        Connecting...
                      </>
                    ) : (
                      <>
                        <Icon name="Wifi" size="sm" className="mr-2" />
                        Connect
                      </>
                    )}
                  </Button>
                </CardFooter>
                <BorderBeam
                  duration={4}
                  reverse
                  colorTo="#3b82f6"
                />
              </Card>
            ) : (
              /* Connected State Card */
              <Card className="relative w-full overflow-hidden">
                <CardHeader>
                  <CardTitle className="flex items-center text-success-600 dark:text-success-400">
                    <Icon name="CheckCircle" size="lg" className="mr-2" />
                    Connected Successfully
                  </CardTitle>
                  <CardDescription>
                    Your Trading 212 API is connected and ready to use.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {auth.authState.accountInfo && (
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Account ID:</span>
                        <span className="font-medium text-gray-900 dark:text-gray-100">{auth.authState.accountInfo.account_id}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Account Type:</span>
                        <span className="font-medium text-gray-900 dark:text-gray-100">{auth.authState.accountInfo.account_type}</span>
                      </div>
                    </div>
                  )}
                </CardContent>
                <CardFooter className="flex justify-between">
                  <Button 
                    variant="outline" 
                    onClick={handleDisconnect}
                    disabled={disconnectMutation.isPending}
                  >
                    {disconnectMutation.isPending ? (
                      <>
                        <Icon name="Refresh" size="sm" animation="spin" className="mr-2" />
                        Disconnecting...
                      </>
                    ) : (
                      <>
                        <Icon name="WifiOff" size="sm" className="mr-2" />
                        Disconnect
                      </>
                    )}
                  </Button>
                  <Button onClick={() => window.location.href = '/dashboard'}>
                    <Icon name="BarChart" size="sm" className="mr-2" />
                    View Dashboard
                  </Button>
                </CardFooter>
                <BorderBeam
                  duration={4}
                  reverse
                  colorTo="#22c55e"
                />
              </Card>
            )}
          </ResponsiveContainer>

          {/* Instructions */}
          <ResponsiveContainer variant="card" animationStyle="from-bottom" animationDelay={0.3}>
            <div className="text-center text-sm text-gray-600 dark:text-gray-400 space-y-2">
              <p>
                <Icon name="Info" size="sm" className="inline mr-1" />
                Get your API key from Trading 212 Settings → API Settings
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500">
                Your API key is encrypted and stored securely
              </p>
            </div>
          </ResponsiveContainer>
        </div>
      )}

      {activeTab === 'preferences' && (
        <ResponsiveContainer variant="card" animationStyle="from-bottom" animationDelay={0.2}>
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">
                Application Preferences
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Dark Mode
                    </label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Toggle between light and dark themes
                    </p>
                  </div>
                  <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-gray-200 dark:bg-gray-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
                    <span className="inline-block h-4 w-4 transform rounded-full bg-white transition-transform translate-x-1" />
                  </button>
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Animations
                    </label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Enable smooth animations and transitions
                    </p>
                  </div>
                  <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-blue-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
                    <span className="inline-block h-4 w-4 transform rounded-full bg-white transition-transform translate-x-6" />
                  </button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Auto Refresh
                    </label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Automatically refresh data during market hours
                    </p>
                  </div>
                  <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-blue-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
                    <span className="inline-block h-4 w-4 transform rounded-full bg-white transition-transform translate-x-6" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </ResponsiveContainer>
      )}

      {activeTab === 'about' && (
        <ResponsiveContainer variant="card" animationStyle="from-bottom" animationDelay={0.2}>
          <div className="space-y-6">
            <div className="text-center">
              <Icon name="BarChart" size="2xl" className="mx-auto text-blue-600 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
                Trading 212 Portfolio Dashboard
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                A comprehensive portfolio analysis and visualization tool for Trading 212 accounts.
              </p>
              <div className="text-xs text-gray-500 dark:text-gray-500">
                Version 1.0.0
              </div>
            </div>
            
            <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
              <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">
                Features
              </h4>
              <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>• Real-time portfolio performance tracking</li>
                <li>• Advanced risk metrics and analysis</li>
                <li>• Visual portfolio allocation insights</li>
                <li>• Historical performance comparisons</li>
                <li>• Dividend income tracking and projections</li>
                <li>• Benchmark comparisons</li>
              </ul>
            </div>
          </div>
        </ResponsiveContainer>
      )}
    </div>
  );
};

export default Settings;