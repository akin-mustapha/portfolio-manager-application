import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import PieList from '../PieList';

// Mock data
const mockPies = [
  {
    id: '1',
    name: 'Growth Pie',
    totalValue: 50000,
    investedAmount: 45000,
    returnAmount: 5000,
    returnPercentage: 11.11,
    updatedAt: '2024-01-15T10:30:00Z'
  },
  {
    id: '2',
    name: 'Dividend Pie',
    totalValue: 30000,
    investedAmount: 32000,
    returnAmount: -2000,
    returnPercentage: -6.25,
    updatedAt: '2024-01-15T10:30:00Z'
  },
  {
    id: '3',
    name: 'Tech Pie',
    totalValue: 0,
    investedAmount: 0,
    returnAmount: 0,
    returnPercentage: 0,
    updatedAt: '2024-01-15T10:30:00Z'
  }
];

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('PieList', () => {
  describe('loading state', () => {
    it('should render loading skeletons when loading is true', () => {
      const { container } = renderWithRouter(
        <PieList pies={[]} loading={true} />
      );
      
      expect(container.querySelectorAll('.animate-pulse')).toHaveLength(3);
      expect(screen.queryByText('Growth Pie')).not.toBeInTheDocument();
    });

    it('should render correct number of loading skeletons', () => {
      const { container } = renderWithRouter(
        <PieList pies={mockPies} loading={true} />
      );
      
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons).toHaveLength(3); // Default skeleton count
    });
  });

  describe('empty state', () => {
    it('should render empty state when no pies provided', () => {
      renderWithRouter(<PieList pies={[]} />);
      
      expect(screen.getByText('No pies found')).toBeInTheDocument();
      expect(screen.getByText('Create pies in your Trading 212 account to see them here')).toBeInTheDocument();
      expect(screen.getByText('🥧')).toBeInTheDocument();
    });

    it('should render empty state when pies is null', () => {
      renderWithRouter(<PieList pies={null as any} />);
      
      expect(screen.getByText('No pies found')).toBeInTheDocument();
    });
  });

  describe('with data', () => {
    it('should render all pie items', () => {
      renderWithRouter(<PieList pies={mockPies} />);
      
      expect(screen.getByText('Growth Pie')).toBeInTheDocument();
      expect(screen.getByText('Dividend Pie')).toBeInTheDocument();
      expect(screen.getByText('Tech Pie')).toBeInTheDocument();
    });

    it('should display pie values correctly', () => {
      renderWithRouter(<PieList pies={mockPies} />);
      
      expect(screen.getByText('Value: £50,000')).toBeInTheDocument();
      expect(screen.getByText('Value: £30,000')).toBeInTheDocument();
      expect(screen.getByText('Value: £0')).toBeInTheDocument();
    });

    it('should display invested amounts correctly', () => {
      renderWithRouter(<PieList pies={mockPies} />);
      
      expect(screen.getByText('Invested: £45,000')).toBeInTheDocument();
      expect(screen.getByText('Invested: £32,000')).toBeInTheDocument();
      expect(screen.getByText('Invested: £0')).toBeInTheDocument();
    });

    it('should display update dates correctly', () => {
      renderWithRouter(<PieList pies={mockPies} />);
      
      // Check that update dates are formatted correctly
      const updateTexts = screen.getAllByText(/Updated:/);
      expect(updateTexts).toHaveLength(3);
    });
  });

  describe('pie status indicators', () => {
    it('should show "Active" status for pies with value', () => {
      renderWithRouter(<PieList pies={mockPies} />);
      
      const activeStatuses = screen.getAllByText('Active');
      expect(activeStatuses).toHaveLength(2); // Growth and Dividend pies
    });

    it('should show "Empty" status for pies without value', () => {
      renderWithRouter(<PieList pies={mockPies} />);
      
      expect(screen.getByText('Empty')).toBeInTheDocument(); // Tech pie
    });
  });

  describe('return formatting', () => {
    it('should format positive returns correctly', () => {
      renderWithRouter(<PieList pies={mockPies} />);
      
      expect(screen.getByText('+£5,000')).toBeInTheDocument();
      expect(screen.getByText('+11.11%')).toBeInTheDocument();
      
      const positiveReturn = screen.getByText('+£5,000').parentElement;
      expect(positiveReturn).toHaveClass('text-green-600');
    });

    it('should format negative returns correctly', () => {
      renderWithRouter(<PieList pies={mockPies} />);
      
      expect(screen.getByText('£2,000')).toBeInTheDocument(); // Uses Math.abs()
      expect(screen.getByText('-6.25%')).toBeInTheDocument();
      
      const negativeReturn = screen.getByText('£2,000').parentElement;
      expect(negativeReturn).toHaveClass('text-red-600');
    });

    it('should format zero returns correctly', () => {
      renderWithRouter(<PieList pies={mockPies} />);
      
      expect(screen.getByText('+£0')).toBeInTheDocument();
      expect(screen.getByText('+0.00%')).toBeInTheDocument();
    });
  });

  describe('maxItems functionality', () => {
    it('should limit displayed items when maxItems is set', () => {
      renderWithRouter(<PieList pies={mockPies} maxItems={2} />);
      
      expect(screen.getByText('Growth Pie')).toBeInTheDocument();
      expect(screen.getByText('Dividend Pie')).toBeInTheDocument();
      expect(screen.queryByText('Tech Pie')).not.toBeInTheDocument();
    });

    it('should show "View all" link when there are more items', () => {
      renderWithRouter(<PieList pies={mockPies} maxItems={2} />);
      
      expect(screen.getByText('View all 3 pies →')).toBeInTheDocument();
    });

    it('should not show "View all" link when showViewAll is false', () => {
      renderWithRouter(
        <PieList pies={mockPies} maxItems={2} showViewAll={false} />
      );
      
      expect(screen.queryByText('View all 3 pies →')).not.toBeInTheDocument();
    });

    it('should show detailed analysis link when all items are shown and more than 3 pies', () => {
      const manyPies = [...mockPies, 
        { ...mockPies[0], id: '4', name: 'Extra Pie' }
      ];
      renderWithRouter(<PieList pies={manyPies} />);
      
      expect(screen.getByText('View detailed analysis →')).toBeInTheDocument();
    });

    it('should not show detailed analysis link when 3 or fewer pies', () => {
      renderWithRouter(<PieList pies={mockPies} />);
      
      expect(screen.queryByText('View detailed analysis →')).not.toBeInTheDocument();
    });
  });

  describe('navigation links', () => {
    it('should link to pie analysis page', () => {
      renderWithRouter(<PieList pies={mockPies} maxItems={2} />);
      
      const viewAllLink = screen.getByText('View all 3 pies →');
      expect(viewAllLink.closest('a')).toHaveAttribute('href', '/pie-analysis');
    });

    it('should link to detailed analysis when available', () => {
      const manyPies = [...mockPies, 
        { ...mockPies[0], id: '4', name: 'Extra Pie' }
      ];
      renderWithRouter(<PieList pies={manyPies} />);
      
      const detailedLink = screen.getByText('View detailed analysis →');
      expect(detailedLink.closest('a')).toHaveAttribute('href', '/pie-analysis');
    });
  });

  describe('hover effects', () => {
    it('should add hover effects to pie items', () => {
      const { container } = renderWithRouter(<PieList pies={mockPies} />);
      
      const pieItems = container.querySelectorAll('.hover\\:border-gray-300');
      expect(pieItems).toHaveLength(mockPies.length);
    });

    it('should add cursor pointer to pie items', () => {
      const { container } = renderWithRouter(<PieList pies={mockPies} />);
      
      const pieItems = container.querySelectorAll('.cursor-pointer');
      expect(pieItems).toHaveLength(mockPies.length);
    });
  });

  describe('text truncation', () => {
    it('should truncate long pie names', () => {
      const longNamePies = [
        {
          ...mockPies[0],
          name: 'Very Long Pie Name That Should Be Truncated Because It Is Too Long'
        }
      ];

      const { container } = renderWithRouter(<PieList pies={longNamePies} />);
      
      const nameElement = container.querySelector('.truncate');
      expect(nameElement).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('should have proper semantic structure', () => {
      renderWithRouter(<PieList pies={mockPies} />);
      
      const pieNames = screen.getAllByRole('heading', { level: 4 });
      expect(pieNames).toHaveLength(mockPies.length);
    });

    it('should be keyboard accessible', () => {
      const manyPies = [...mockPies, 
        { ...mockPies[0], id: '4', name: 'Extra Pie' }
      ];
      const { container } = renderWithRouter(<PieList pies={manyPies} />);
      
      const pieItems = container.querySelectorAll('a');
      expect(pieItems.length).toBeGreaterThan(0);
    });
  });

  describe('edge cases', () => {
    it('should handle pies without update dates', () => {
      const piesWithoutDates = mockPies.map(pie => ({ ...pie, updatedAt: '' }));
      
      renderWithRouter(<PieList pies={piesWithoutDates} />);
      
      expect(screen.queryByText(/Updated:/)).not.toBeInTheDocument();
    });

    it('should handle very large numbers', () => {
      const largePies = [
        {
          ...mockPies[0],
          totalValue: 1234567890,
          investedAmount: 1000000000,
          returnAmount: 234567890
        }
      ];

      renderWithRouter(<PieList pies={largePies} />);
      
      expect(screen.getByText('Value: £1,234,567,890')).toBeInTheDocument();
      expect(screen.getByText('Invested: £1,000,000,000')).toBeInTheDocument();
      expect(screen.getByText('+£234,567,890')).toBeInTheDocument();
    });

    it('should handle decimal percentages correctly', () => {
      const decimalPies = [
        {
          ...mockPies[0],
          returnPercentage: 5.555555
        }
      ];

      renderWithRouter(<PieList pies={decimalPies} />);
      
      expect(screen.getByText('+5.56%')).toBeInTheDocument(); // Rounded to 2 decimals
    });
  });
});