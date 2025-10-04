import { useState, useEffect } from 'react';
import { AuthState } from '../types/api';

const AUTH_STORAGE_KEY = 'trading212_auth';

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>(() => {
    // Initialize from localStorage
    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    if (stored) {
      try {
        return JSON.parse(stored);
      } catch {
        return {
          isAuthenticated: false,
          connectionStatus: 'disconnected' as const,
        };
      }
    }
    return {
      isAuthenticated: false,
      connectionStatus: 'disconnected' as const,
    };
  });

  // Persist auth state to localStorage
  useEffect(() => {
    localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(authState));
  }, [authState]);

  const setApiKey = (apiKey: string) => {
    setAuthState(prev => ({
      ...prev,
      apiKey,
      isAuthenticated: true,
      connectionStatus: 'connected',
      lastConnected: new Date(),
    }));
  };

  const clearAuth = () => {
    setAuthState({
      isAuthenticated: false,
      connectionStatus: 'disconnected',
    });
    localStorage.removeItem(AUTH_STORAGE_KEY);
  };

  const setConnectionStatus = (status: AuthState['connectionStatus']) => {
    setAuthState(prev => ({
      ...prev,
      connectionStatus: status,
    }));
  };

  return {
    authState,
    setApiKey,
    clearAuth,
    setConnectionStatus,
    isAuthenticated: authState.isAuthenticated,
    connectionStatus: authState.connectionStatus,
  };
};