import { useEffect } from 'react';
import { useAppContext } from '../contexts/AppContext';

export const useAuthError = () => {
  const { auth } = useAppContext();

  useEffect(() => {
    const handleAuthError = () => {
      auth.clearAuth();
      auth.setConnectionStatus('error');
    };

    window.addEventListener('auth-error', handleAuthError);

    return () => {
      window.removeEventListener('auth-error', handleAuthError);
    };
  }, [auth]);
};