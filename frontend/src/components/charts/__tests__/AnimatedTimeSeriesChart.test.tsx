import React from 'react';
import { render, screen } from '@testing-library/react';
import AnimatedTimeSeriesChart, { TimeSeriesDataPoint } from '../AnimatedTimeSeriesChart';

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    h3: ({ children, ...props }: any) => <h3 {...props}>{children}</h3>,
    circle: ({ children, ...props }: any) => <circle {...props}>{children}</circle>,
  },
  AnimatePresence: ({ children }: any) => children,
}));

// Mock recharts
jest.mock('recharts', () => ({
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  ResponsiveContainer: ({ children }: any) => <div data-testid="responsive-container">{children}</div>,
  ReferenceLine: () => <div data-testid="reference-line" />,
}));

// Mock date-fns
jest.mock('date-fns', () => ({
  format: jest.fn((date, formatStr) => '2023-01-01'),
  parseISO: jest.fn((dateStr) => new Date(dateStr)),
}));

const mockData: TimeSeriesDataPoint[] = [
  { date: '2023-01-01', value: 1000, label: 'Test point 1' },
  { date: '2023-01-02', value: 1100, label: 'Test point 2' },
  { date: '2023-01-03', value: 1050, label: 'Test point 3' },
];

describe('AnimatedTimeSeriesChart', () => {
  it('renders loading state', () => {
    render(<AnimatedTimeSeriesChart data={[]} loading={true} />);
    
    // Should show loading skeleton
    expect(screen.getByText('Loading data...')).toBeInTheDocument();
  });

  it('renders empty state when no data', () => {
    render(<AnimatedTimeSeriesChart data={[]} loading={false} />);
    
    expect(screen.getByText('No data available')).toBeInTheDocument();
    expect(screen.getByText('Time series data will appear here')).toBeInTheDocument();
  });

  it('renders chart with data', () => {
    render(<AnimatedTimeSeriesChart data={mockData} loading={false} />);
    
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
    expect(screen.getByTestId('line-chart')).toBeInTheDocument();
    expect(screen.getByTestId('line')).toBeInTheDocument();
  });

  it('renders with title', () => {
    const title = 'Test Chart Title';
    render(<AnimatedTimeSeriesChart data={mockData} title={title} loading={false} />);
    
    expect(screen.getByText(title)).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const customClass = 'custom-chart-class';
    const { container } = render(
      <AnimatedTimeSeriesChart data={mockData} className={customClass} loading={false} />
    );
    
    expect(container.firstChild?.firstChild).toHaveClass(customClass);
  });
});