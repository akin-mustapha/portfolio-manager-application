import React from 'react';
import { render, screen } from '@testing-library/react';
import PieChart from '../PieChart';

describe('PieChart', () => {
  const mockData = [
    { name: 'Growth Pie', value: 50000, percentage: 50 },
    { name: 'Dividend Pie', value: 30000, percentage: 30 },
    { name: 'Tech Pie', value: 20000, percentage: 20 },
  ];

  describe('loading state', () => {
    it('should render loading skeleton when loading is true', () => {
      const { container } = render(
        <PieChart data={[]} loading={true} />
      );
      
      expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
      expect(container.querySelector('.bg-gray-200.rounded-full')).toBeInTheDocument();
    });

    it('should not render data when loading', () => {
      render(<PieChart data={mockData} loading={true} />);
      
      expect(screen.queryByText('Growth Pie')).not.toBeInTheDocument();
    });
  });

  describe('empty state', () => {
    it('should render empty state when no data provided', () => {
      render(<PieChart data={[]} />);
      
      expect(screen.getByText('No portfolio data available')).toBeInTheDocument();
      expect(screen.getByText('Connect your Trading 212 API to view allocation')).toBeInTheDocument();
      expect(screen.getByText('📊')).toBeInTheDocument();
    });

    it('should render empty state when data is null', () => {
      render(<PieChart data={null as any} />);
      
      expect(screen.getByText('No portfolio data available')).toBeInTheDocument();
    });
  });

  describe('with data', () => {
    it('should render SVG pie chart', () => {
      const { container } = render(<PieChart data={mockData} />);
      
      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
      expect(svg).toHaveAttribute('width', '200');
      expect(svg).toHaveAttribute('height', '200');
    });

    it('should render pie slices for each data item', () => {
      const { container } = render(<PieChart data={mockData} />);
      
      const paths = container.querySelectorAll('path');
      expect(paths).toHaveLength(mockData.length);
    });

    it('should render legend with all pie names', () => {
      render(<PieChart data={mockData} />);
      
      expect(screen.getByText('Growth Pie')).toBeInTheDocument();
      expect(screen.getByText('Dividend Pie')).toBeInTheDocument();
      expect(screen.getByText('Tech Pie')).toBeInTheDocument();
    });

    it('should display percentages in legend', () => {
      render(<PieChart data={mockData} />);
      
      expect(screen.getByText('50.0%')).toBeInTheDocument();
      expect(screen.getByText('30.0%')).toBeInTheDocument();
      expect(screen.getByText('20.0%')).toBeInTheDocument();
    });

    it('should display values in legend', () => {
      render(<PieChart data={mockData} />);
      
      expect(screen.getByText('£50,000')).toBeInTheDocument();
      expect(screen.getByText('£30,000')).toBeInTheDocument();
      expect(screen.getByText('£20,000')).toBeInTheDocument();
    });

    it('should display total portfolio value', () => {
      render(<PieChart data={mockData} />);
      
      expect(screen.getByText('Total Portfolio')).toBeInTheDocument();
      expect(screen.getByText('£100,000')).toBeInTheDocument();
    });

    it('should display pie count summary', () => {
      render(<PieChart data={mockData} />);
      
      expect(screen.getByText('3 pies • Live allocation')).toBeInTheDocument();
    });

    it('should handle singular pie count', () => {
      const singlePieData = [mockData[0]];
      render(<PieChart data={singlePieData} />);
      
      expect(screen.getByText('1 pie • Live allocation')).toBeInTheDocument();
    });
  });

  describe('color assignment', () => {
    it('should assign different colors to pie slices', () => {
      const { container } = render(<PieChart data={mockData} />);
      
      const colorDots = container.querySelectorAll('.w-3.h-3.rounded-full');
      expect(colorDots).toHaveLength(mockData.length);
      
      // Check that each dot has a different background color
      const colors = Array.from(colorDots).map(dot => 
        (dot as HTMLElement).style.backgroundColor
      );
      const uniqueColors = new Set(colors);
      expect(uniqueColors.size).toBe(mockData.length);
    });
  });

  describe('tooltips and hover effects', () => {
    it('should add hover effects to pie slices', () => {
      const { container } = render(<PieChart data={mockData} />);
      
      const paths = container.querySelectorAll('path');
      paths.forEach(path => {
        expect(path).toHaveClass('hover:opacity-80', 'transition-opacity', 'cursor-pointer');
      });
    });

    it('should add tooltips to pie slices', () => {
      const { container } = render(<PieChart data={mockData} />);
      
      const titles = container.querySelectorAll('title');
      expect(titles).toHaveLength(mockData.length);
      
      expect(titles[0]).toHaveTextContent('Growth Pie: 50.0%');
      expect(titles[1]).toHaveTextContent('Dividend Pie: 30.0%');
      expect(titles[2]).toHaveTextContent('Tech Pie: 20.0%');
    });
  });

  describe('legend interactions', () => {
    it('should add hover effects to legend items', () => {
      const { container } = render(<PieChart data={mockData} />);
      
      const legendItems = container.querySelectorAll('.hover\\:bg-gray-50');
      expect(legendItems).toHaveLength(mockData.length);
    });

    it('should truncate long pie names with title attribute', () => {
      const longNameData = [
        { name: 'Very Long Pie Name That Should Be Truncated', value: 50000, percentage: 100 }
      ];
      
      const { container } = render(<PieChart data={longNameData} />);
      
      const nameElement = container.querySelector('.truncate');
      expect(nameElement).toBeInTheDocument();
      expect(nameElement).toHaveAttribute('title', 'Very Long Pie Name That Should Be Truncated');
    });
  });

  describe('custom height', () => {
    it('should use default height when not specified', () => {
      const { container } = render(<PieChart data={[]} />);
      
      const chartContainer = container.firstChild as HTMLElement;
      expect(chartContainer.style.height).toBe('300px');
    });

    it('should use custom height when specified', () => {
      const { container } = render(<PieChart data={[]} height={400} />);
      
      const chartContainer = container.firstChild as HTMLElement;
      expect(chartContainer.style.height).toBe('400px');
    });
  });

  describe('scrollable legend', () => {
    it('should make legend scrollable when many items', () => {
      const { container } = render(<PieChart data={mockData} />);
      
      const legendContainer = container.querySelector('.max-h-48.overflow-y-auto');
      expect(legendContainer).toBeInTheDocument();
    });
  });

  describe('edge cases', () => {
    it('should handle zero values', () => {
      const zeroData = [
        { name: 'Empty Pie', value: 0, percentage: 0 }
      ];
      
      render(<PieChart data={zeroData} />);
      
      expect(screen.getByText('Empty Pie')).toBeInTheDocument();
      expect(screen.getByText('0.0%')).toBeInTheDocument();
      expect(screen.getByText('£0')).toBeInTheDocument();
    });

    it('should handle very small percentages', () => {
      const smallData = [
        { name: 'Small Pie', value: 1, percentage: 0.01 }
      ];
      
      render(<PieChart data={smallData} />);
      
      expect(screen.getByText('0.0%')).toBeInTheDocument(); // Rounded to 1 decimal
    });

    it('should handle large numbers with proper formatting', () => {
      const largeData = [
        { name: 'Large Pie', value: 1234567, percentage: 100 }
      ];
      
      render(<PieChart data={largeData} />);
      
      expect(screen.getByText('£1,234,567')).toBeInTheDocument();
    });
  });
});