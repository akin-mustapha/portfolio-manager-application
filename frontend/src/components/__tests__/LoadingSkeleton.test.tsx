import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import LoadingSkeleton from '../LoadingSkeleton';

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

describe('LoadingSkeleton', () => {
  it('renders basic rectangle skeleton', () => {
    const { container } = render(
      <LoadingSkeleton variant="rectangle" width="200px" height="100px" />
    );

    const skeletonElement = container.querySelector('.bg-gray-200');
    expect(skeletonElement).toBeInTheDocument();
    expect(skeletonElement).toHaveStyle({ width: '200px', height: '100px' });
  });

  it('renders circle skeleton', () => {
    const { container } = render(
      <LoadingSkeleton variant="circle" width="50px" height="50px" />
    );

    const skeletonElement = container.querySelector('.rounded-full');
    expect(skeletonElement).toBeInTheDocument();
  });

  it('renders text skeleton', () => {
    const { container } = render(
      <LoadingSkeleton variant="text" width="150px" />
    );

    const skeletonElement = container.querySelector('.bg-gray-200');
    expect(skeletonElement).toBeInTheDocument();
    expect(skeletonElement).toHaveStyle({ width: '150px' });
  });

  it('renders card skeleton with multiple elements', () => {
    const { container } = render(
      <LoadingSkeleton variant="card" />
    );

    // Should have multiple skeleton elements for card structure
    const skeletonElements = container.querySelectorAll('.bg-gray-200');
    expect(skeletonElements.length).toBeGreaterThan(3);
  });

  it('renders chart skeleton', () => {
    const { container } = render(
      <LoadingSkeleton variant="chart" />
    );

    // Should have chart-specific elements
    const chartContainer = container.querySelector('.h-64');
    expect(chartContainer).toBeInTheDocument();
  });

  it('renders table skeleton with specified rows', () => {
    const { container } = render(
      <LoadingSkeleton variant="table" rows={3} />
    );

    // Should have table structure with specified number of rows
    const tableRows = container.querySelectorAll('.grid-cols-4');
    expect(tableRows.length).toBeGreaterThanOrEqual(3);
  });

  it('renders dashboard skeleton with specified columns', () => {
    const { container } = render(
      <LoadingSkeleton variant="dashboard" columns={4} />
    );

    // Should have dashboard structure
    const dashboardContainer = container.querySelector('.space-y-6');
    expect(dashboardContainer).toBeInTheDocument();
  });

  it('includes shimmer animation by default', () => {
    const { container } = render(
      <LoadingSkeleton variant="rectangle" />
    );

    const shimmerElement = container.querySelector('.animate-shimmer');
    expect(shimmerElement).toBeInTheDocument();
  });

  it('can disable animation', () => {
    const { container } = render(
      <LoadingSkeleton variant="rectangle" animate={false} />
    );

    const shimmerElement = container.querySelector('.animate-shimmer');
    expect(shimmerElement).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <LoadingSkeleton variant="rectangle" className="custom-class" />
    );

    const skeletonElement = container.querySelector('.custom-class');
    expect(skeletonElement).toBeInTheDocument();
  });
});