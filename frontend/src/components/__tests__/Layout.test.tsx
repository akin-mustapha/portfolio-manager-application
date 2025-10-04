import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import Layout from '../Layout';

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

// Mock ConnectionStatus component
jest.mock('../ConnectionStatus', () => {
  return function MockConnectionStatus({ size }: { size?: string }) {
    return <div data-testid="connection-status" data-size={size}>Connection Status</div>;
  };
});

const renderWithRouter = (component: React.ReactElement, initialRoute = '/') => {
  return render(
    <MemoryRouter initialEntries={[initialRoute]}>
      {component}
    </MemoryRouter>
  );
};

describe('Layout', () => {
  const mockChildren = <div data-testid="test-content">Test Content</div>;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('basic rendering', () => {
    it('should render children content', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      expect(screen.getByTestId('test-content')).toBeInTheDocument();
    });

    it('should render main navigation items', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
      expect(screen.getByText('API Setup')).toBeInTheDocument();
      expect(screen.getByText('Pie Analysis')).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();
    });

    it('should render application title', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      expect(screen.getByText('T212 Dashboard')).toBeInTheDocument();
    });

    it('should render connection status', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      expect(screen.getByTestId('connection-status')).toBeInTheDocument();
      expect(screen.getByTestId('connection-status')).toHaveAttribute('data-size', 'sm');
    });

    it('should render refresh button', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      expect(screen.getByRole('button', { name: 'Refresh' })).toBeInTheDocument();
    });
  });

  describe('navigation highlighting', () => {
    it('should highlight Dashboard when on root path', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>, '/');
      
      const dashboardLink = screen.getByText('Dashboard').closest('a');
      expect(dashboardLink).toHaveClass('bg-blue-100', 'text-blue-700');
    });

    it('should highlight Dashboard when on /dashboard path', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>, '/dashboard');
      
      const dashboardLink = screen.getByText('Dashboard').closest('a');
      expect(dashboardLink).toHaveClass('bg-blue-100', 'text-blue-700');
    });

    it('should highlight API Setup when on /api-setup path', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>, '/api-setup');
      
      const apiSetupLink = screen.getByText('API Setup').closest('a');
      expect(apiSetupLink).toHaveClass('bg-blue-100', 'text-blue-700');
    });

    it('should highlight Pie Analysis when on /pie-analysis path', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>, '/pie-analysis');
      
      const pieAnalysisLink = screen.getByText('Pie Analysis').closest('a');
      expect(pieAnalysisLink).toHaveClass('bg-blue-100', 'text-blue-700');
    });

    it('should highlight Settings when on /settings path', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>, '/settings');
      
      const settingsLink = screen.getByText('Settings').closest('a');
      expect(settingsLink).toHaveClass('bg-blue-100', 'text-blue-700');
    });

    it('should not highlight any item when on unknown path', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>, '/unknown');
      
      const dashboardLink = screen.getByText('Dashboard').closest('a');
      const apiSetupLink = screen.getByText('API Setup').closest('a');
      
      expect(dashboardLink).not.toHaveClass('bg-blue-100', 'text-blue-700');
      expect(apiSetupLink).not.toHaveClass('bg-blue-100', 'text-blue-700');
    });
  });

  describe('mobile sidebar', () => {
    it('should not show mobile sidebar by default', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      expect(screen.queryByText('Menu')).not.toBeInTheDocument();
    });

    it('should show mobile menu button on mobile', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      const menuButton = screen.getByRole('button', { name: '☰' });
      expect(menuButton).toBeInTheDocument();
      expect(menuButton).toHaveClass('lg:hidden');
    });

    it('should open mobile sidebar when menu button is clicked', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      const menuButton = screen.getByRole('button', { name: '☰' });
      fireEvent.click(menuButton);
      
      expect(screen.getByText('Menu')).toBeInTheDocument();
    });

    it('should close mobile sidebar when close button is clicked', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      // Open sidebar
      const menuButton = screen.getByRole('button', { name: '☰' });
      fireEvent.click(menuButton);
      
      // Close sidebar
      const closeButton = screen.getByRole('button', { name: '✕' });
      fireEvent.click(closeButton);
      
      expect(screen.queryByText('Menu')).not.toBeInTheDocument();
    });

    it('should close mobile sidebar when overlay is clicked', () => {
      const { container } = renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      // Open sidebar
      const menuButton = screen.getByRole('button', { name: '☰' });
      fireEvent.click(menuButton);
      
      // Click overlay
      const overlay = container.querySelector('.bg-gray-600.bg-opacity-75');
      expect(overlay).toBeInTheDocument();
      fireEvent.click(overlay!);
      
      expect(screen.queryByText('Menu')).not.toBeInTheDocument();
    });

    it('should close mobile sidebar when navigation link is clicked', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      // Open sidebar
      const menuButton = screen.getByRole('button', { name: '☰' });
      fireEvent.click(menuButton);
      
      // Click navigation link in mobile sidebar
      const mobileNavLinks = screen.getAllByText('Dashboard');
      const mobileDashboardLink = mobileNavLinks.find(link => 
        link.closest('.lg\\:hidden') !== null
      );
      
      if (mobileDashboardLink) {
        fireEvent.click(mobileDashboardLink);
        expect(screen.queryByText('Menu')).not.toBeInTheDocument();
      }
    });
  });

  describe('desktop sidebar', () => {
    it('should render desktop sidebar', () => {
      const { container } = renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      const desktopSidebar = container.querySelector('.lg\\:fixed.lg\\:inset-y-0');
      expect(desktopSidebar).toBeInTheDocument();
    });

    it('should render navigation icons', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      expect(screen.getByText('📊')).toBeInTheDocument(); // Dashboard icon
      expect(screen.getByText('🔑')).toBeInTheDocument(); // API Setup icon
      expect(screen.getByText('🥧')).toBeInTheDocument(); // Pie Analysis icon
      expect(screen.getByText('⚙️')).toBeInTheDocument(); // Settings icon
    });
  });

  describe('header', () => {
    it('should render API status label', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      expect(screen.getByText('API Status:')).toBeInTheDocument();
    });

    it('should render mobile title on mobile', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      expect(screen.getByText('Trading 212 Portfolio Dashboard')).toBeInTheDocument();
    });

    it('should have proper header styling', () => {
      const { container } = renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      const header = container.querySelector('header');
      expect(header).toHaveClass('bg-white', 'shadow-sm', 'border-b', 'border-gray-200');
    });
  });

  describe('main content area', () => {
    it('should have proper main content styling', () => {
      const { container } = renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      const main = container.querySelector('main');
      expect(main).toHaveClass('py-6', 'px-4', 'sm:px-6', 'lg:px-8');
    });

    it('should have proper layout with desktop sidebar offset', () => {
      const { container } = renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      const contentArea = container.querySelector('.lg\\:pl-64');
      expect(contentArea).toBeInTheDocument();
    });
  });

  describe('responsive design', () => {
    it('should hide desktop sidebar on mobile', () => {
      const { container } = renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      const desktopSidebar = container.querySelector('.hidden.lg\\:fixed');
      expect(desktopSidebar).toBeInTheDocument();
    });

    it('should show mobile menu button only on mobile', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      const menuButton = screen.getByRole('button', { name: '☰' });
      expect(menuButton).toHaveClass('lg:hidden');
    });

    it('should hide mobile title on desktop', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      const mobileTitle = screen.getByText('Trading 212 Portfolio Dashboard');
      expect(mobileTitle).toHaveClass('lg:hidden');
    });
  });

  describe('accessibility', () => {
    it('should have proper semantic structure', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      expect(screen.getByRole('main')).toBeInTheDocument();
      expect(screen.getByRole('banner')).toBeInTheDocument(); // header
      expect(screen.getByRole('navigation')).toBeInTheDocument();
    });

    it('should have proper heading hierarchy', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      const headings = screen.getAllByRole('heading');
      expect(headings.length).toBeGreaterThan(0);
    });

    it('should have keyboard accessible navigation', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      const links = screen.getAllByRole('link');
      links.forEach(link => {
        expect(link).toHaveAttribute('href');
      });
    });

    it('should have accessible buttons', () => {
      renderWithRouter(<Layout>{mockChildren}</Layout>);
      
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button).toBeInTheDocument();
      });
    });
  });

  describe('edge cases', () => {
    it('should handle empty children', () => {
      renderWithRouter(<Layout>{null}</Layout>);
      
      const main = screen.getByRole('main');
      expect(main).toBeInTheDocument();
    });

    it('should handle multiple children', () => {
      renderWithRouter(
        <Layout>
          <div data-testid="child1">Child 1</div>
          <div data-testid="child2">Child 2</div>
        </Layout>
      );
      
      expect(screen.getByTestId('child1')).toBeInTheDocument();
      expect(screen.getByTestId('child2')).toBeInTheDocument();
    });
  });
});