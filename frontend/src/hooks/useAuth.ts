import { useState, useEffect, useCallback } from 'react';
import { AuthState, SessionResponse, Trading212APIResponse } from '../types/api';
import { apiService } from '../services/api';

const AUTH_STORAGE_KEY = 'trading212_auth';

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>(() => {
    // Initialize from localStorage
    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    if (stored) {
      try {
        const parsedState = JSON.parse(stored);
        // Check if token is expired
        if (parsedState.tokenExpiresAt) {
          const expiresAt = new Date(parsedState.tokenExpiresAt);
          if (expiresAt <= new Date()) {
            // Token expired, clear auth
            localStorage.removeItem(AUTH_STORAGE_KEY);
            return {
              isAuthenticated: false,
              connectionStatus: 'disconnected' as const,
            };
          }
        }
        return parsedState;
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

  // Initialize session if not authenticated
  const initializeSession = useCallback(async (sessionName?: string) => {
    try {
      const response = await apiService.createSession({ sessionName });
      const sessionData = response.data;
      
      const newAuthState: AuthState = {
        isAuthenticated: true,
        sessionId: sessionData.sessionId,
        accessToken: sessionData.accessToken,
        refreshToken: sessionData.refreshToken,
        tokenExpiresAt: new Date(Date.now() + sessionData.expiresIn * 1000),
        connectionStatus: 'disconnected',
        lastConnected: sessionData.createdAt,
        sessionName: sessionName,
      };
      
      setAuthState(newAuthState);
      return sessionData;
    } catch (error) {
      console.error('Failed to initialize session:', error);
      throw error;
    }
  }, []);

  const setupTrading212API = useCallback(async (apiKey: string, validateConnection = true) => {
    try {
      setConnectionStatus('connecting');
      
      // Ensure we have a session first
      if (!authState.sessionId) {
        await initializeSession();
      }
      
      const response = await apiService.setupTrading212API({
        apiKey,
        validateConnection
      });
      
      const setupData = response.data;
      
      setAuthState(prev => ({
        ...prev,
        apiKey,
        connectionStatus: 'connected',
        lastConnected: new Date(),
        accountInfo: setupData.accountInfo,
      }));
      
      return setupData;
    } catch (error) {
      setConnectionStatus('error');
      throw error;
    }
  }, [authState.sessionId, initializeSession]);

  const validateTrading212API = useCallback(async (apiKey: string) => {
    try {
      const response = await apiService.validateTrading212API({
        apiKey,
        validateConnection: true
      });
      return response.data;
    } catch (error) {
      console.error('API validation failed:', error);
      throw error;
    }
  }, []);

  const setApiKey = (apiKey: string) => {
    setAuthState(prev => ({
      ...prev,
      apiKey,
      connectionStatus: 'connected',
      lastConnected: new Date(),
    }));
  };

  const clearAuth = useCallback(async () => {
    try {
      if (authState.sessionId) {
        await apiService.deleteSession();
      }
    } catch (error) {
      console.warn('Failed to delete session:', error);
    } finally {
      setAuthState({
        isAuthenticated: false,
        connectionStatus: 'disconnected',
      });
      localStorage.removeItem(AUTH_STORAGE_KEY);
    }
  }, [authState.sessionId]);

  const disconnectTrading212 = useCallback(async () => {
    try {
      await apiService.removeTrading212API();
      setAuthState(prev => ({
        ...prev,
        apiKey: undefined,
        connectionStatus: 'disconnected',
        accountInfo: undefined,
      }));
    } catch (error) {
      console.error('Failed to disconnect Trading 212:', error);
      throw error;
    }
  }, []);

  const setConnectionStatus = (status: AuthState['connectionStatus']) => {
    setAuthState(prev => ({
      ...prev,
      connectionStatus: status,
    }));
  };

  const isTokenExpired = useCallback(() => {
    if (!authState.tokenExpiresAt) return false;
    return new Date(authState.tokenExpiresAt) <= new Date();
  }, [authState.tokenExpiresAt]);

  return {
    authState,
    initializeSession,
    setupTrading212API,
    validateTrading212API,
    setApiKey,
    clearAuth,
    disconnectTrading212,
    setConnectionStatus,
    isAuthenticated: authState.isAuthenticated,
    connectionStatus: authState.connectionStatus,
    isTokenExpired,
    hasTrading212Connection: !!authState.apiKey && authState.connectionStatus === 'connected',
  };
};