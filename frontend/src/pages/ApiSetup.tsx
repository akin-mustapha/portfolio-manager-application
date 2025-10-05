import React, { useState, useEffect } from 'react';
import { useAppContext } from '../contexts/AppContext';
import { useMutation } from '@tanstack/react-query';
import { Icon } from '../components/icons';
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

const ApiSetup: React.FC = () => {
  const { auth } = useAppContext();
  const [apiKey, setApiKey] = useState('');
  const [sessionName, setSessionName] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [isConnected, setIsConnected] = useState(false);

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
        color: 'text-green-600',
        icon: <Icon name="CheckCircle" size="sm" className="text-green-500" />
      };
    } else if (setupMutation.isPending) {
      return {
        text: 'Connecting...',
        color: 'text-yellow-600',
        icon: <Icon name="Refresh" size="sm" animation="spin" className="text-yellow-500" />
      };
    } else {
      return {
        text: 'Not Connected',
        color: 'text-gray-600',
        icon: <Icon name="AlertCircle" size="sm" className="text-gray-500" />
      };
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-md mx-auto space-y-6">
        {/* Connection Status */}
        <div className="text-center">
          <div className="flex items-center justify-center mb-2">
            {getConnectionStatus().icon}
            <span className={`ml-2 text-sm font-medium ${getConnectionStatus().color}`}>
              {getConnectionStatus().text}
            </span>
          </div>
        </div>

        {/* Error Display */}
        {errors.length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <Icon name="AlertTriangle" size="sm" className="text-red-400 mr-2 mt-0.5" />
              <div>
                <h4 className="text-sm font-medium text-red-800">
                  {errors.length === 1 ? 'Error' : 'Errors'}
                </h4>
                <ul className="mt-1 text-sm text-red-700">
                  {errors.map((error, index) => (
                    <li key={index}>• {error}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Main Form Card */}
        {!isConnected ? (
          <Card className="relative w-full overflow-hidden">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Icon name="Key" size="lg" className="mr-2 text-blue-600" />
                Connect Trading 212
              </CardTitle>
              <CardDescription>
                Enter your session name and API key to access your portfolio data.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit}>
                <div className="grid w-full items-center gap-4">
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
              <CardTitle className="flex items-center text-green-600">
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
                    <span className="text-gray-600">Account ID:</span>
                    <span className="font-medium">{auth.authState.accountInfo.account_id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Account Type:</span>
                    <span className="font-medium">{auth.authState.accountInfo.account_type}</span>
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

        {/* Instructions */}
        <div className="text-center text-sm text-gray-600 space-y-2">
          <p>
            <Icon name="Info" size="sm" className="inline mr-1" />
            Get your API key from Trading 212 Settings → API Settings
          </p>
          <p className="text-xs text-gray-500">
            Your API key is encrypted and stored securely
          </p>
        </div>
      </div>
    </div>
  );
};

export default ApiSetup;