import React from 'react';
import { render, screen } from '@testing-library/react';
import ConnectionStatus from '../ConnectionStatus';

// Mock the useAppContext hook
const mockAuth = {
  authState: {
    isAuthenticated: false,
    connectionStatus: 'disconnected' as const,
  },
  initializeSession: jest.fn(),
  setupTrading212API: jest.fn(),
  validateTrading212API: jest.fn(),
  setApiKey: jest.fn(),
  clearAuth: jest.fn(),
  disconnectTrading212: jest.fn(),
  setConnectionStatus: jest.fn(),
  isAuthenticated: false,
  connectionStatus: 'disconnected' as const,
  isTokenExpired: jest.fn(() => false),
  hasTrading212Connection: false,
};

jest.mock('../../contexts/AppContext', () => ({
  useAppContext: () => ({ auth: mockAuth }),
}));

describe('ConnectionStatus', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset to default state
    mockAuth.isAuthenticated = false;
    mockAuth.authState.isAuthenticated = false;
    mockAuth.hasTrading212Connection = false;
    mockAuth.connectionStatus = 'disconnected';
    mockAuth.authState.connectionStatus = 'disconnected';
  });

  describe('when not authenticated', () => {
    it('should render "No Session" status', () => {
      render(<ConnectionStatus />);
      
      expect(screen.getByText('No Session')).toBeInTheDocument();
    });

    it('should show gray dot for no session', () => {
      const { container } = render(<ConnectionStatus />);
      
      const dot = container.querySelector('.bg-gray-400');
      expect(dot).toBeInTheDocument();
    });

    it('should have gray text color', () => {
      render(<ConnectionStatus />);
      
      const statusText = screen.getByText('No Session');
      expect(statusText).toHaveClass('text-gray-500');
    });
  });

  describe('when authenticated but no Trading 212 connection', () => {
    beforeEach(() => {
      mockAuth.isAuthenticated = true;
      mockAuth.authState.isAuthenticated = true;
      mockAuth.hasTrading212Connection = false;
    });

    it('should render "Session Active" status', () => {
      render(<ConnectionStatus />);
      
      expect(screen.getByText('Session Active')).toBeInTheDocument();
    });

    it('should show yellow dot for session active', () => {
      const { container } = render(<ConnectionStatus />);
      
      const dot = container.querySelector('.bg-yellow-500');
      expect(dot).toBeInTheDocument();
    });

    it('should have yellow text color', () => {
      render(<ConnectionStatus />);
      
      const statusText = screen.getByText('Session Active');
      expect(statusText).toHaveClass('text-yellow-600');
    });
  });

  describe('when fully connected', () => {
    beforeEach(() => {
      mockAuth.isAuthenticated = true;
      mockAuth.authState.isAuthenticated = true;
      mockAuth.hasTrading212Connection = true;
      mockAuth.connectionStatus = 'connected';
      mockAuth.authState.connectionStatus = 'connected';
    });

    it('should render "Connected" status', () => {
      render(<ConnectionStatus />);
      
      expect(screen.getByText('Connected')).toBeInTheDocument();
    });

    it('should show green dot for connected', () => {
      const { container } = render(<ConnectionStatus />);
      
      const dot = container.querySelector('.bg-green-500');
      expect(dot).toBeInTheDocument();
    });

    it('should have green text color', () => {
      render(<ConnectionStatus />);
      
      const statusText = screen.getByText('Connected');
      expect(statusText).toHaveClass('text-green-600');
    });
  });

  describe('when connecting', () => {
    beforeEach(() => {
      mockAuth.isAuthenticated = true;
      mockAuth.authState.isAuthenticated = true;
      mockAuth.hasTrading212Connection = true;
      mockAuth.connectionStatus = 'connecting';
      mockAuth.authState.connectionStatus = 'connecting';
    });

    it('should render "Connecting..." status', () => {
      render(<ConnectionStatus />);
      
      expect(screen.getByText('Connecting...')).toBeInTheDocument();
    });

    it('should show pulsing yellow dot for connecting', () => {
      const { container } = render(<ConnectionStatus />);
      
      const dot = container.querySelector('.bg-yellow-500.animate-pulse');
      expect(dot).toBeInTheDocument();
    });

    it('should have yellow text color', () => {
      render(<ConnectionStatus />);
      
      const statusText = screen.getByText('Connecting...');
      expect(statusText).toHaveClass('text-yellow-600');
    });
  });

  describe('when connection error', () => {
    beforeEach(() => {
      mockAuth.isAuthenticated = true;
      mockAuth.authState.isAuthenticated = true;
      mockAuth.hasTrading212Connection = true;
      mockAuth.connectionStatus = 'error';
      mockAuth.authState.connectionStatus = 'error';
    });

    it('should render "Connection Error" status', () => {
      render(<ConnectionStatus />);
      
      expect(screen.getByText('Connection Error')).toBeInTheDocument();
    });

    it('should show red dot for error', () => {
      const { container } = render(<ConnectionStatus />);
      
      const dot = container.querySelector('.bg-red-500');
      expect(dot).toBeInTheDocument();
    });

    it('should have red text color', () => {
      render(<ConnectionStatus />);
      
      const statusText = screen.getByText('Connection Error');
      expect(statusText).toHaveClass('text-red-600');
    });
  });

  describe('size variations', () => {
    it('should render small size correctly', () => {
      const { container } = render(<ConnectionStatus size="sm" />);
      
      const dot = container.querySelector('.w-2.h-2');
      expect(dot).toBeInTheDocument();
      
      const text = screen.getByText('No Session');
      expect(text).toHaveClass('text-xs');
    });

    it('should render large size correctly', () => {
      const { container } = render(<ConnectionStatus size="lg" />);
      
      const dot = container.querySelector('.w-4.h-4');
      expect(dot).toBeInTheDocument();
      
      const text = screen.getByText('No Session');
      expect(text).toHaveClass('text-base');
    });

    it('should render medium size by default', () => {
      const { container } = render(<ConnectionStatus />);
      
      const dot = container.querySelector('.w-3.h-3');
      expect(dot).toBeInTheDocument();
      
      const text = screen.getByText('No Session');
      expect(text).toHaveClass('text-sm');
    });
  });

  describe('text visibility', () => {
    it('should show text by default', () => {
      render(<ConnectionStatus />);
      
      expect(screen.getByText('No Session')).toBeInTheDocument();
    });

    it('should hide text when showText is false', () => {
      render(<ConnectionStatus showText={false} />);
      
      expect(screen.queryByText('No Session')).not.toBeInTheDocument();
    });
  });
});