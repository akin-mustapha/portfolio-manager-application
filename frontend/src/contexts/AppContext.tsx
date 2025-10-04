import React, { createContext, useContext, ReactNode } from 'react';
import { useAuth } from '../hooks/useAuth';
import { AuthState } from '../types/api';

interface AppContextType {
  auth: {
    authState: AuthState;
    initializeSession: (sessionName?: string) => Promise<any>;
    setupTrading212API: (apiKey: string, validateConnection?: boolean) => Promise<any>;
    validateTrading212API: (apiKey: string) => Promise<any>;
    setApiKey: (apiKey: string) => void;
    clearAuth: () => Promise<void>;
    disconnectTrading212: () => Promise<void>;
    setConnectionStatus: (status: AuthState['connectionStatus']) => void;
    isAuthenticated: boolean;
    connectionStatus: AuthState['connectionStatus'];
    isTokenExpired: () => boolean;
    hasTrading212Connection: boolean;
  };
}

const AppContext = createContext<AppContextType | undefined>(undefined);

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const auth = useAuth();

  const value: AppContextType = {
    auth,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};