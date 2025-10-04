import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ApiSetup from '../ApiSetup';

// Mock the useAppContext hook
const mockAuth = {
  authState: {
    isAuthenticated: false,
    connectionStatus: 'disconnected' as const,
    accountInfo: undefined,
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

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('ApiSetup', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset mock auth state
    mockAuth.isAuthenticated = false;
    mockAuth.authState.isAuthenticated = false;
    mockAuth.authState.connectionStatus = 'disconnected';
    mockAuth.authState.accountInfo = undefined;
    mockAuth.connectionStatus = 'disconnected';
    mockAuth.hasTrading212Connection = false;
  });

  it('should render session creation step when not authenticated', () => {
    renderWithProviders(<ApiSetup />);

    expect(screen.getByText('Step 1: Create Session')).toBeInTheDocument();
    expect(screen.getByText('Session Name (Optional)')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '🚀 Create Session' })).toBeInTheDocument();
  });

  it('should render API setup step when authenticated but no Trading 212 connection', () => {
    mockAuth.isAuthenticated = true;
    mockAuth.authState.isAuthenticated = true;
    mockAuth.connectionStatus = 'disconnected';
    mockAuth.hasTrading212Connection = false;

    renderWithProviders(<ApiSetup />);

    expect(screen.getByText('Step 2: Trading 212 API Configuration')).toBeInTheDocument();
    expect(screen.getByText('Trading 212 API Key')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '🔗 Connect to Trading 212' })).toBeInTheDocument();
  });

  it('should render complete step when fully connected', () => {
    mockAuth.isAuthenticated = true;
    mockAuth.authState.isAuthenticated = true;
    mockAuth.authState.connectionStatus = 'connected';
    mockAuth.hasTrading212Connection = true;
    mockAuth.connectionStatus = 'connected';

    renderWithProviders(<ApiSetup />);

    expect(screen.getByText('Connection Complete')).toBeInTheDocument();
    expect(screen.getByText('Successfully Connected')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: '🔍 Test Connection' })).toBeInTheDocument();
  });

  it('should show connection status correctly', () => {
    mockAuth.isAuthenticated = false;
    mockAuth.connectionStatus = 'disconnected';

    renderWithProviders(<ApiSetup />);

    expect(screen.getByText('No session')).toBeInTheDocument();
  });

  it('should handle session creation', async () => {
    mockAuth.initializeSession.mockResolvedValue({ sessionId: 'test-session' });

    renderWithProviders(<ApiSetup />);

    const sessionNameInput = screen.getByPlaceholderText('e.g., My Portfolio Dashboard');
    const createButton = screen.getByRole('button', { name: '🚀 Create Session' });

    fireEvent.change(sessionNameInput, { target: { value: 'Test Session' } });
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(mockAuth.initializeSession).toHaveBeenCalledWith('Test Session');
    });
  });

  it('should handle API key setup', async () => {
    mockAuth.isAuthenticated = true;
    mockAuth.authState.isAuthenticated = true;
    mockAuth.authState.connectionStatus = 'disconnected';
    mockAuth.connectionStatus = 'disconnected';
    mockAuth.hasTrading212Connection = false;
    mockAuth.setupTrading212API.mockResolvedValue({ status: 'success' });

    renderWithProviders(<ApiSetup />);

    const apiKeyInput = screen.getByPlaceholderText('Enter your Trading 212 API key');
    const connectButton = screen.getByRole('button', { name: '🔗 Connect to Trading 212' });

    fireEvent.change(apiKeyInput, { target: { value: 'test-api-key' } });
    fireEvent.click(connectButton);

    await waitFor(() => {
      expect(mockAuth.setupTrading212API).toHaveBeenCalledWith('test-api-key', true);
    });
  });

  it('should toggle API key visibility', () => {
    mockAuth.isAuthenticated = true;
    mockAuth.authState.isAuthenticated = true;
    mockAuth.authState.connectionStatus = 'disconnected';
    mockAuth.connectionStatus = 'disconnected';
    mockAuth.hasTrading212Connection = false;

    renderWithProviders(<ApiSetup />);

    const apiKeyInput = screen.getByPlaceholderText('Enter your Trading 212 API key');
    const toggleButton = screen.getByRole('button', { name: '👁️' });

    expect(apiKeyInput).toHaveAttribute('type', 'password');

    fireEvent.click(toggleButton);

    expect(apiKeyInput).toHaveAttribute('type', 'text');
  });

  it('should display errors when API key is empty', async () => {
    mockAuth.isAuthenticated = true;
    mockAuth.authState.isAuthenticated = true;
    mockAuth.authState.connectionStatus = 'disconnected';
    mockAuth.connectionStatus = 'disconnected';
    mockAuth.hasTrading212Connection = false;

    renderWithProviders(<ApiSetup />);

    const connectButton = screen.getByRole('button', { name: '🔗 Connect to Trading 212' });

    // The button should be disabled when API key is empty
    expect(connectButton).toBeDisabled();
  });

  it('should show account information when available', () => {
    mockAuth.isAuthenticated = true;
    mockAuth.authState.isAuthenticated = true;
    mockAuth.authState.connectionStatus = 'connected';
    mockAuth.authState.accountInfo = {
      accountId: 'test-account-id',
      accountType: 'equity',
    };
    mockAuth.hasTrading212Connection = true;
    mockAuth.connectionStatus = 'connected';

    renderWithProviders(<ApiSetup />);

    expect(screen.getByText('Account Information')).toBeInTheDocument();
    expect(screen.getByText('Account ID: test-account-id')).toBeInTheDocument();
    expect(screen.getByText('Account Type: equity')).toBeInTheDocument();
  });

  it('should handle disconnect', async () => {
    mockAuth.isAuthenticated = true;
    mockAuth.authState.isAuthenticated = true;
    mockAuth.authState.connectionStatus = 'connected';
    mockAuth.hasTrading212Connection = true;
    mockAuth.connectionStatus = 'connected';
    mockAuth.disconnectTrading212.mockResolvedValue({});

    renderWithProviders(<ApiSetup />);

    const disconnectButton = screen.getByRole('button', { name: '🔌 Disconnect API' });

    fireEvent.click(disconnectButton);

    await waitFor(() => {
      expect(mockAuth.disconnectTrading212).toHaveBeenCalled();
    });
  });

  it('should display error messages when API setup fails', async () => {
    mockAuth.isAuthenticated = true;
    mockAuth.authState.isAuthenticated = true;
    mockAuth.authState.connectionStatus = 'disconnected';
    mockAuth.connectionStatus = 'disconnected';
    mockAuth.hasTrading212Connection = false;
    mockAuth.setupTrading212API.mockRejectedValue(new Error('Invalid API key'));

    renderWithProviders(<ApiSetup />);

    const apiKeyInput = screen.getByPlaceholderText('Enter your Trading 212 API key');
    const connectButton = screen.getByRole('button', { name: '🔗 Connect to Trading 212' });

    fireEvent.change(apiKeyInput, { target: { value: 'invalid-key' } });
    fireEvent.click(connectButton);

    await waitFor(() => {
      expect(screen.getByText('Invalid API key')).toBeInTheDocument();
    });
  });

  it('should show connecting status during API setup', async () => {
    mockAuth.isAuthenticated = true;
    mockAuth.authState.isAuthenticated = true;
    mockAuth.authState.connectionStatus = 'connecting';
    mockAuth.connectionStatus = 'connecting';
    mockAuth.hasTrading212Connection = false;

    renderWithProviders(<ApiSetup />);

    expect(screen.getByText('Session active, Trading 212 not connected')).toBeInTheDocument();
  });

  it('should handle session creation with custom name', async () => {
    // Ensure we're in session creation step
    mockAuth.isAuthenticated = false;
    mockAuth.authState.isAuthenticated = false;
    mockAuth.initializeSession.mockResolvedValue({ sessionId: 'test-session' });

    renderWithProviders(<ApiSetup />);

    const sessionNameInput = screen.getByPlaceholderText('e.g., My Portfolio Dashboard');
    const createButton = screen.getByRole('button', { name: '🚀 Create Session' });

    fireEvent.change(sessionNameInput, { target: { value: 'Custom Session Name' } });
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(mockAuth.initializeSession).toHaveBeenCalledWith('Custom Session Name');
    });
  });

  it('should handle session creation without custom name', async () => {
    // Ensure we're in session creation step
    mockAuth.isAuthenticated = false;
    mockAuth.authState.isAuthenticated = false;
    mockAuth.initializeSession.mockResolvedValue({ sessionId: 'test-session' });

    renderWithProviders(<ApiSetup />);

    const createButton = screen.getByRole('button', { name: '🚀 Create Session' });

    fireEvent.click(createButton);

    await waitFor(() => {
      expect(mockAuth.initializeSession).toHaveBeenCalledWith('Portfolio Dashboard Session');
    });
  });

  it('should handle full reset', async () => {
    mockAuth.isAuthenticated = true;
    mockAuth.authState.isAuthenticated = true;
    mockAuth.authState.connectionStatus = 'connected';
    mockAuth.hasTrading212Connection = true;
    mockAuth.connectionStatus = 'connected';
    mockAuth.clearAuth.mockResolvedValue();

    renderWithProviders(<ApiSetup />);

    const resetButton = screen.getByRole('button', { name: '🔄 Reset All' });

    fireEvent.click(resetButton);

    await waitFor(() => {
      expect(mockAuth.clearAuth).toHaveBeenCalled();
    });
  });

  it('should validate API connection', async () => {
    mockAuth.isAuthenticated = true;
    mockAuth.authState.isAuthenticated = true;
    mockAuth.authState.connectionStatus = 'connected';
    mockAuth.authState.apiKey = 'test-api-key';
    mockAuth.hasTrading212Connection = true;
    mockAuth.connectionStatus = 'connected';
    mockAuth.validateTrading212API.mockResolvedValue({ isValid: true });

    renderWithProviders(<ApiSetup />);

    const testButton = screen.getByRole('button', { name: '🔍 Test Connection' });

    fireEvent.click(testButton);

    await waitFor(() => {
      expect(mockAuth.validateTrading212API).toHaveBeenCalledWith('test-api-key');
    });
  });
});