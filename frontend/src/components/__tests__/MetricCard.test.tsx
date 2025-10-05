import React from 'react';
import { render, screen } from '@testing-library/react';
import MetricCard from '../MetricCard';

describe('MetricCard', () => {
  const defaultProps = {
    title: 'Total Value',
    value: '£125,000',
  };

  it('should render basic metric card with title and value', () => {
    render(<MetricCard {...defaultProps} />);
    
    expect(screen.getByText('Total Value')).toBeInTheDocument();
    expect(screen.getByText('£125,000')).toBeInTheDocument();
  });

  it('should render subtitle when provided', () => {
    render(
      <MetricCard 
        {...defaultProps} 
        subtitle="As of today" 
      />
    );
    
    expect(screen.getByText('As of today')).toBeInTheDocument();
  });

  it('should render icon when provided', () => {
    render(
      <MetricCard 
        {...defaultProps} 
        icon="💰" 
      />
    );
    
    expect(screen.getByText('💰')).toBeInTheDocument();
  });

  describe('loading state', () => {
    it('should render loading skeleton when loading is true', () => {
      const { container } = render(
        <MetricCard {...defaultProps} loading={true} />
      );
      
      expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
      expect(screen.queryByText('TOTAL VALUE')).not.toBeInTheDocument();
      expect(screen.queryByText('£125,000')).not.toBeInTheDocument();
    });

    it('should render content when loading is false', () => {
      render(<MetricCard {...defaultProps} loading={false} />);
      
      expect(screen.getByText('Total Value')).toBeInTheDocument();
      expect(screen.getByText('£125,000')).toBeInTheDocument();
    });
  });

  describe('trend indicators', () => {
    it('should render positive trend correctly', () => {
      const trend = {
        value: 5.2,
        isPositive: true,
        prefix: '+',
        suffix: '%'
      };

      render(
        <MetricCard 
          {...defaultProps} 
          trend={trend} 
        />
      );
      
      expect(screen.getByLabelText('arrow up right')).toBeInTheDocument();
      expect(screen.getByText('+5.2%')).toBeInTheDocument();
      
      const trendElement = screen.getByText('+5.2%').closest('.text-green-600');
      expect(trendElement).toBeInTheDocument();
    });

    it('should render negative trend correctly', () => {
      const trend = {
        value: -3.1,
        isPositive: false,
        prefix: '',
        suffix: '%'
      };

      render(
        <MetricCard 
          {...defaultProps} 
          trend={trend} 
        />
      );
      
      expect(screen.getByLabelText('arrow down right')).toBeInTheDocument();
      expect(screen.getByText('3.1%')).toBeInTheDocument(); // Absolute value
      
      const trendElement = screen.getByText('3.1%').closest('.text-red-600');
      expect(trendElement).toBeInTheDocument();
    });

    it('should format trend value with thousands separator', () => {
      const trend = {
        value: 1250.75,
        isPositive: true,
        prefix: '£',
        suffix: ''
      };

      render(
        <MetricCard 
          {...defaultProps} 
          trend={trend} 
        />
      );
      
      expect(screen.getByText('£1,250.75')).toBeInTheDocument(); // Not rounded, uses exact value
    });

    it('should handle trend without prefix and suffix', () => {
      const trend = {
        value: 42,
        isPositive: true
      };

      render(
        <MetricCard 
          {...defaultProps} 
          trend={trend} 
        />
      );
      
      expect(screen.getByText('42')).toBeInTheDocument();
    });
  });

  describe('styling and layout', () => {
    it('should have proper CSS classes for card styling', () => {
      const { container } = render(<MetricCard {...defaultProps} />);
      
      const card = container.firstChild;
      expect(card).toHaveClass('bg-white', 'rounded-lg', 'shadow', 'p-6');
    });

    it('should have hover effect', () => {
      const { container } = render(<MetricCard {...defaultProps} />);
      
      const card = container.firstChild;
      expect(card).toHaveClass('hover:shadow-md', 'transition-shadow');
    });

    it('should format title as uppercase', () => {
      render(<MetricCard title="portfolio value" value="£100,000" />);
      
      const titleElement = screen.getByText('portfolio value');
      expect(titleElement).toHaveClass('uppercase');
    });

    it('should style value text correctly', () => {
      render(<MetricCard {...defaultProps} />);
      
      const valueElement = screen.getByText('£125,000');
      expect(valueElement).toHaveClass('text-2xl', 'font-bold', 'text-gray-900');
    });

    it('should style subtitle correctly', () => {
      render(
        <MetricCard 
          {...defaultProps} 
          subtitle="Last updated 5 minutes ago" 
        />
      );
      
      const subtitleElement = screen.getByText('Last updated 5 minutes ago');
      expect(subtitleElement).toHaveClass('text-sm', 'text-gray-500');
    });
  });

  describe('accessibility', () => {
    it('should have proper semantic structure', () => {
      render(<MetricCard {...defaultProps} />);
      
      // Title should be in a heading-like element
      const titleElement = screen.getByText('Total Value');
      expect(titleElement.tagName).toBe('H3');
      
      // Value should be in a paragraph
      const valueElement = screen.getByText('£125,000');
      expect(valueElement.tagName).toBe('P');
    });

    it('should be keyboard accessible', () => {
      const { container } = render(<MetricCard {...defaultProps} />);
      
      const card = container.firstChild as HTMLElement;
      expect(card.tabIndex).toBe(-1); // Should be focusable but not in tab order by default
    });
  });

  describe('edge cases', () => {
    it('should handle empty title', () => {
      render(<MetricCard title="" value="£100,000" />);
      
      expect(screen.getByText('£100,000')).toBeInTheDocument();
    });

    it('should handle empty value', () => {
      render(<MetricCard title="Total Value" value="" />);
      
      expect(screen.getByText('Total Value')).toBeInTheDocument();
    });

    it('should handle zero trend value', () => {
      const trend = {
        value: 0,
        isPositive: true,
        suffix: '%'
      };

      render(
        <MetricCard 
          {...defaultProps} 
          trend={trend} 
        />
      );
      
      expect(screen.getByText('0%')).toBeInTheDocument();
    });
  });
});