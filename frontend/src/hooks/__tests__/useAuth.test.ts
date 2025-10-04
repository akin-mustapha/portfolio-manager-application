import { renderHook, act } from '@testing-library/react';
import { useAuth } from '../useAuth';

// Mock the API service
jest.mock('../../services/api', () => ({
  apiService: {
    createSession: jest.fn(),
    setupTrading212API: jest.fn(),
    validateTrading212API: jest.fn(),
    removeTrading212API: jest.fn(),
    deleteSession: jest.fn(),
  },
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('useAuth', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  it('should initialize with default state when no stored auth', () => {
    const { result } = renderHook(() => useAuth());

    expect(result.current.authState).toEqual({
      isAuthenticated: false,
      connectionStatus: 'disconnected',
    });
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.hasTrading212Connection).toBe(false);
  });

  it('should initialize with stored auth state', () => {
    const storedAuth = {
      isAuthenticated: true,
      sessionId: 'test-session',
      accessToken: 'test-token',
      refreshToken: 'test-refresh',
      tokenExpiresAt: new Date(Date.now() + 3600000).toISOString(), // 1 hour from now
      connectionStatus: 'connected',
      apiKey: 'test-api-key',
    };
    
    localStorageMock.getItem.mockReturnValue(JSON.stringify(storedAuth));

    const { result } = renderHook(() => useAuth());

    expect(result.current.authState.isAuthenticated).toBe(true);
    expect(result.current.authState.sessionId).toBe('test-session');
    expect(result.current.hasTrading212Connection).toBe(true);
  });

  it('should clear expired tokens on initialization', () => {
    const expiredAuth = {
      isAuthenticated: true,
      sessionId: 'test-session',
      accessToken: 'test-token',
      tokenExpiresAt: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
      connectionStatus: 'connected',
    };
    
    localStorageMock.getItem.mockReturnValue(JSON.stringify(expiredAuth));

    const { result } = renderHook(() => useAuth());

    expect(result.current.authState.isAuthenticated).toBe(false);
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('trading212_auth');
  });

  it('should detect token expiration', () => {
    const { result } = renderHook(() => useAuth());

    // Set expired token
    act(() => {
      result.current.authState.tokenExpiresAt = new Date(Date.now() - 1000);
    });

    expect(result.current.isTokenExpired()).toBe(true);
  });

  it('should update connection status', () => {
    const { result } = renderHook(() => useAuth());

    act(() => {
      result.current.setConnectionStatus('connecting');
    });

    expect(result.current.connectionStatus).toBe('connecting');
  });

  it('should persist auth state to localStorage', () => {
    const { result } = renderHook(() => useAuth());

    act(() => {
      result.current.setConnectionStatus('connected');
    });

    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'trading212_auth',
      expect.stringContaining('"connectionStatus":"connected"')
    );
  });
});