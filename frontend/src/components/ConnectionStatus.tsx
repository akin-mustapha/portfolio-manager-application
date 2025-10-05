import React from 'react';
import { useAppContext } from '../contexts/AppContext';
import { Icon, StatusIcon } from './icons';

interface ConnectionStatusProps {
  showText?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'dot' | 'icon';
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({ 
  showText = true, 
  size = 'md',
  variant = 'dot'
}) => {
  const { auth } = useAppContext();

  const getStatusColor = () => {
    if (!auth.isAuthenticated) return 'bg-gray-400';
    if (!auth.hasTrading212Connection) return 'bg-yellow-500';
    
    switch (auth.connectionStatus) {
      case 'connected': return 'bg-green-500';
      case 'connecting': return 'bg-yellow-500 animate-pulse';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-400';
    }
  };

  const getStatusText = () => {
    if (!auth.isAuthenticated) return 'No Session';
    if (!auth.hasTrading212Connection) return 'Session Active';
    
    switch (auth.connectionStatus) {
      case 'connected': return 'Connected';
      case 'connecting': return 'Connecting...';
      case 'error': return 'Connection Error';
      default: return 'Not Connected';
    }
  };

  const getTextColor = () => {
    if (!auth.isAuthenticated) return 'text-gray-500';
    if (!auth.hasTrading212Connection) return 'text-yellow-600';
    
    switch (auth.connectionStatus) {
      case 'connected': return 'text-green-600';
      case 'connecting': return 'text-yellow-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-500';
    }
  };

  const getDotSize = () => {
    switch (size) {
      case 'sm': return 'w-2 h-2';
      case 'lg': return 'w-4 h-4';
      default: return 'w-3 h-3';
    }
  };

  const getTextSize = () => {
    switch (size) {
      case 'sm': return 'text-xs';
      case 'lg': return 'text-base';
      default: return 'text-sm';
    }
  };

  const getStatusIcon = () => {
    if (!auth.isAuthenticated) return 'XCircle';
    if (!auth.hasTrading212Connection) return 'Clock';
    
    switch (auth.connectionStatus) {
      case 'connected': return 'CheckCircle';
      case 'connecting': return 'Clock';
      case 'error': return 'AlertCircle';
      default: return 'XCircle';
    }
  };

  const getIconColor = () => {
    if (!auth.isAuthenticated) return 'text-gray-500';
    if (!auth.hasTrading212Connection) return 'text-yellow-500';
    
    switch (auth.connectionStatus) {
      case 'connected': return 'text-green-500';
      case 'connecting': return 'text-yellow-500';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getIconSize = () => {
    switch (size) {
      case 'sm': return 'sm' as const;
      case 'lg': return 'lg' as const;
      default: return 'md' as const;
    }
  };

  return (
    <div className="flex items-center space-x-2">
      {variant === 'icon' ? (
        <Icon 
          name={getStatusIcon() as any}
          size={getIconSize()}
          className={getIconColor()}
          animation={auth.connectionStatus === 'connecting' ? 'pulse' : 'none'}
          ariaLabel={`Connection status: ${getStatusText()}`}
        />
      ) : (
        <div className={`rounded-full ${getDotSize()} ${getStatusColor()}`} />
      )}
      {showText && (
        <span className={`${getTextColor()} ${getTextSize()}`}>
          {getStatusText()}
        </span>
      )}
    </div>
  );
};

export default ConnectionStatus;