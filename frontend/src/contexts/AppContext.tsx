import React, { createContext, useContext, ReactNode } from 'react';
import { useAuth } from '../hooks/useAuth';
import { AuthState } from '../types/api';

interface AppContextType {
  auth: {
    authState: AuthState;
    setApiKey: (apiKey: string) => void;
    clearAuth: () => void;
    setConnectionStatus: (status: AuthState['connectionStatus']) => void;
    isAuthenticated: boolean;
    connectionStatus: AuthState['connectionStatus'];
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