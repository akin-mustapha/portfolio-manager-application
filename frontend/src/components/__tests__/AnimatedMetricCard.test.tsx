import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import AnimatedMetricCard from '../AnimatedMetricCard';
import { Icon } from '../icons';

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    p: ({ children, ...props }: any) => <p {...props}>{children}</p>,
    h3: ({ children, ...props }: any) => <h3 {...props}>{children}</h3>,
  },
  useAnimation: () => ({
    start: jest.fn(),
  }),
  useInView: () => true,
  useReducedMotion: () => false,
}));

describe('AnimatedMetricCard', () => {
  it('renders basic metric card with title and value', () => {
    render(
      <AnimatedMetricCard
        title="Total Value"
        value="£125,430"
      />
    );

    expect(screen.getByText('Total Value')).toBeInTheDocument();
    expect(screen.getByText('£125,430')).toBeInTheDocument();
  });

  it('renders with trend data', () => {
    render(
      <AnimatedMetricCard
        title="Total Return"
        value="25.43%"
        trend={{
          value: 25430,
          isPositive: true,
          prefix: '£'
        }}
      />
    );

    expect(screen.getByText('Total Return')).toBeInTheDocument();
    expect(screen.getByText('25.43%')).toBeInTheDocument();
    expect(screen.getByText('£25,430')).toBeInTheDocument();
  });

  it('renders with subtitle', () => {
    render(
      <AnimatedMetricCard
        title="Total Invested"
        value="£100,000"
        subtitle="Capital deployed"
      />
    );

    expect(screen.getByText('Total Invested')).toBeInTheDocument();
    expect(screen.getByText('£100,000')).toBeInTheDocument();
    expect(screen.getByText('Capital deployed')).toBeInTheDocument();
  });

  it('renders with icon', () => {
    render(
      <AnimatedMetricCard
        title="Active Pies"
        value="4"
        icon={<Icon name="PieChart" size="lg" />}
      />
    );

    expect(screen.getByText('Active Pies')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
  });

  it('renders loading state with shimmer skeleton', () => {
    render(
      <AnimatedMetricCard
        title="Loading..."
        value="--"
        loading={true}
      />
    );

    // Should render skeleton elements
    const skeletonElements = document.querySelectorAll('.animate-shimmer');
    expect(skeletonElements.length).toBeGreaterThan(0);
  });

  it('handles numeric value animation', () => {
    render(
      <AnimatedMetricCard
        title="Portfolio Value"
        value={125430.50}
      />
    );

    expect(screen.getByText('Portfolio Value')).toBeInTheDocument();
    // The animated value should be rendered
    expect(screen.getByText('125,431')).toBeInTheDocument();
  });

  it('applies gradient styling when enabled', () => {
    const { container } = render(
      <AnimatedMetricCard
        title="Test Card"
        value="100"
        gradient={true}
      />
    );

    const cardElement = container.firstChild as HTMLElement;
    expect(cardElement).toHaveClass('bg-gradient-to-br');
  });

  it('handles click events when clickable', () => {
    const handleClick = jest.fn();
    
    render(
      <AnimatedMetricCard
        title="Clickable Card"
        value="100"
        onClick={handleClick}
      />
    );

    const cardElement = screen.getByText('Clickable Card').closest('div');
    expect(cardElement).toHaveClass('cursor-pointer');
  });
});