import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ApiSetup from '../ApiSetup';

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
  });

  it('should render session creation step when not authenticated', () => {
    renderWithProviders(<ApiSetup />);

    expect(screen.getByText('Step 1: Create Session')).toBeInTheDocument();
    expect(screen.getByText('Session Name (Optional)')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create Session' })).toBeInTheDocument();
  });

  it('should render API setup step when authenticated but no Trading 212 connection', () => {
    mockAuth.isAuthenticated = true;
    mockAuth.authState.isAuthenticated = true;
    mockAuth.hasTrading212Connection = false;

    renderWithProviders(<ApiSetup />);

    expect(screen.getByText('Step 2: Trading 212 API Configuration')).toBeInTheDocument();
    expect(screen.getByText('Trading 212 API Key')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Connect to Trading 212' })).toBeInTheDocument();
  });

  it('should render complete step when fully connected', () => {
    mockAuth.isAuthenticated = true;
    mockAuth.authState.isAuthenticated = true;
    mockAuth.hasTrading212Connection = true;
    mockAuth.connectionStatus = 'connected';

    renderWithProviders(<ApiSetup />);

    expect(screen.getByText('Connection Complete')).toBeInTheDocument();
    expect(screen.getByText('Successfully Connected')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Test Connection' })).toBeInTheDocument();
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
    const createButton = screen.getByRole('button', { name: 'Create Session' });

    fireEvent.change(sessionNameInput, { target: { value: 'Test Session' } });
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(mockAuth.initializeSession).toHaveBeenCalledWith('Test Session');
    });
  });

  it('should handle API key setup', async () => {
    mockAuth.isAuthenticated = true;
    mockAuth.authState.isAuthenticated = true;
    mockAuth.hasTrading212Connection = false;
    mockAuth.setupTrading212API.mockResolvedValue({ status: 'success' });

    renderWithProviders(<ApiSetup />);

    const apiKeyInput = screen.getByPlaceholderText('Enter your Trading 212 API key');
    const connectButton = screen.getByRole('button', { name: 'Connect to Trading 212' });

    fireEvent.change(apiKeyInput, { target: { value: 'test-api-key' } });
    fireEvent.click(connectButton);

    await waitFor(() => {
      expect(mockAuth.setupTrading212API).toHaveBeenCalledWith('test-api-key', true);
    });
  });

  it('should toggle API key visibility', () => {
    mockAuth.isAuthenticated = true;
    mockAuth.authState.isAuthenticated = true;
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
    mockAuth.hasTrading212Connection = false;

    renderWithProviders(<ApiSetup />);

    const connectButton = screen.getByRole('button', { name: 'Connect to Trading 212' });

    fireEvent.click(connectButton);

    await waitFor(() => {
      expect(screen.getByText('API key is required')).toBeInTheDocument();
    });
  });

  it('should show account information when available', () => {
    mockAuth.isAuthenticated = true;
    mockAuth.authState.isAuthenticated = true;
    mockAuth.hasTrading212Connection = true;
    mockAuth.connectionStatus = 'connected';
    mockAuth.authState.accountInfo = {
      accountId: 'test-account-id',
      accountType: 'equity',
    };

    renderWithProviders(<ApiSetup />);

    expect(screen.getByText('Account Information')).toBeInTheDocument();
    expect(screen.getByText('Account ID: test-account-id')).toBeInTheDocument();
    expect(screen.getByText('Account Type: equity')).toBeInTheDocument();
  });

  it('should handle disconnect', async () => {
    mockAuth.isAuthenticated = true;
    mockAuth.authState.isAuthenticated = true;
    mockAuth.hasTrading212Connection = true;
    mockAuth.connectionStatus = 'connected';
    mockAuth.disconnectTrading212.mockResolvedValue({});

    renderWithProviders(<ApiSetup />);

    const disconnectButton = screen.getByRole('button', { name: 'Disconnect Trading 212' });

    fireEvent.click(disconnectButton);

    await waitFor(() => {
      expect(mockAuth.disconnectTrading212).toHaveBeenCalled();
    });
  });
});