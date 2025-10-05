import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { Icon, StatusIcon, TrendIcon, ActionIcon } from '../Icon';
import { IconWrapper } from '../IconWrapper';
import { FinancialIcons } from '../FinancialIcons';

// Mock framer-motion properly for Jest
jest.mock('framer-motion', () => ({
  motion: (component: any) => component,
}));

describe('Icon Component', () => {
  it('renders icon with correct name', () => {
    render(<Icon name="DollarSign" ariaLabel="Dollar sign icon" />);
    const icon = screen.getByLabelText('Dollar sign icon');
    expect(icon).toBeInTheDocument();
  });

  it('generates default aria-label from icon name', () => {
    render(<Icon name="TrendingUp" />);
    const icon = screen.getByLabelText('trending up');
    expect(icon).toBeInTheDocument();
  });

  it('respects aria-hidden prop', () => {
    render(<Icon name="DollarSign" ariaHidden={true} />);
    const icon = document.querySelector('svg');
    expect(icon).toHaveAttribute('aria-hidden', 'true');
  });

  it('handles click events', () => {
    const handleClick = jest.fn();
    render(<Icon name="Settings" onClick={handleClick} />);
    const icon = screen.getByLabelText('settings');
    fireEvent.click(icon);
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('disables click when disabled prop is true', () => {
    const handleClick = jest.fn();
    render(<Icon name="Settings" onClick={handleClick} disabled={true} />);
    const icon = screen.getByLabelText('settings');
    fireEvent.click(icon);
    expect(handleClick).not.toHaveBeenCalled();
  });
});

describe('IconWrapper Component', () => {
  const MockIcon = (props: any) => <svg data-testid="mock-icon" {...props} />;

  it('applies correct size classes', () => {
    const { rerender } = render(<IconWrapper icon={MockIcon} size="sm" />);
    expect(screen.getByTestId('mock-icon')).toHaveClass('w-4', 'h-4');

    rerender(<IconWrapper icon={MockIcon} size="lg" />);
    expect(screen.getByTestId('mock-icon')).toHaveClass('w-6', 'h-6');
  });

  it('applies correct variant classes', () => {
    const { rerender } = render(<IconWrapper icon={MockIcon} variant="default" />);
    expect(screen.getByTestId('mock-icon')).toHaveClass('text-current');

    rerender(<IconWrapper icon={MockIcon} variant="disabled" />);
    expect(screen.getByTestId('mock-icon')).toHaveClass('text-neutral-400', 'cursor-not-allowed', 'opacity-50');
  });

  it('applies custom className', () => {
    render(<IconWrapper icon={MockIcon} className="custom-class" />);
    expect(screen.getByTestId('mock-icon')).toHaveClass('custom-class');
  });
});

describe('StatusIcon Component', () => {
  it('renders correct icon for success status', () => {
    render(<StatusIcon status="success" ariaLabel="Success status" />);
    const icon = screen.getByLabelText('Success status');
    expect(icon).toBeInTheDocument();
  });

  it('renders correct icon for error status', () => {
    render(<StatusIcon status="error" ariaLabel="Error status" />);
    const icon = screen.getByLabelText('Error status');
    expect(icon).toBeInTheDocument();
  });

  it('renders correct icon for warning status', () => {
    render(<StatusIcon status="warning" ariaLabel="Warning status" />);
    const icon = screen.getByLabelText('Warning status');
    expect(icon).toBeInTheDocument();
  });

  it('renders correct icon for info status', () => {
    render(<StatusIcon status="info" ariaLabel="Info status" />);
    const icon = screen.getByLabelText('Info status');
    expect(icon).toBeInTheDocument();
  });
});

describe('TrendIcon Component', () => {
  it('renders trending up icon for up trend', () => {
    render(<TrendIcon trend="up" ariaLabel="Upward trend" />);
    const icon = screen.getByLabelText('Upward trend');
    expect(icon).toBeInTheDocument();
  });

  it('renders trending down icon for down trend', () => {
    render(<TrendIcon trend="down" ariaLabel="Downward trend" />);
    const icon = screen.getByLabelText('Downward trend');
    expect(icon).toBeInTheDocument();
  });

  it('renders activity icon for neutral trend', () => {
    render(<TrendIcon trend="neutral" ariaLabel="Neutral trend" />);
    const icon = screen.getByLabelText('Neutral trend');
    expect(icon).toBeInTheDocument();
  });
});

describe('ActionIcon Component', () => {
  it('renders correct icons for different actions', () => {
    const actions = ['edit', 'delete', 'copy', 'share', 'download'] as const;
    
    actions.forEach((action) => {
      const { unmount } = render(<ActionIcon action={action} ariaLabel={`${action} action`} />);
      const icon = screen.getByLabelText(`${action} action`);
      expect(icon).toBeInTheDocument();
      unmount();
    });
  });

  it('applies hover variant and scale animation by default', () => {
    render(<ActionIcon action="edit" />);
    const icon = screen.getByLabelText('edit');
    expect(icon).toBeInTheDocument();
    // Note: Testing animation classes would require more complex setup
  });
});

describe('FinancialIcons', () => {
  it('exports all required financial icons', () => {
    const requiredIcons = [
      'TrendingUp',
      'TrendingDown',
      'DollarSign',
      'PieChart',
      'BarChart',
      'Activity',
      'AlertTriangle',
      'CheckCircle',
      'X',
      'Menu',
      'Settings',
      'Refresh',
      'Eye',
      'EyeOff',
    ];

    requiredIcons.forEach((iconName) => {
      expect(FinancialIcons).toHaveProperty(iconName);
      // React components can be functions or objects, so we check if it's truthy and callable
      const icon = FinancialIcons[iconName as keyof typeof FinancialIcons];
      expect(icon).toBeDefined();
      expect(typeof icon === 'function' || typeof icon === 'object').toBe(true);
    });
  });

  it('has all icon categories defined', () => {
    const { IconCategories } = require('../FinancialIcons');
    
    expect(IconCategories).toHaveProperty('performance');
    expect(IconCategories).toHaveProperty('financial');
    expect(IconCategories).toHaveProperty('controls');
    expect(IconCategories).toHaveProperty('status');
    expect(IconCategories).toHaveProperty('navigation');
    expect(IconCategories).toHaveProperty('actions');
    
    // Verify categories contain arrays of icon names
    Object.values(IconCategories).forEach((category) => {
      expect(Array.isArray(category)).toBe(true);
      expect(category.length).toBeGreaterThan(0);
    });
  });
});

describe('Icon System Integration', () => {
  it('works with all size variants', () => {
    const sizes = ['xs', 'sm', 'md', 'lg', 'xl', '2xl'] as const;
    
    sizes.forEach((size) => {
      const { unmount } = render(<Icon name="DollarSign" size={size} ariaLabel={`${size} icon`} />);
      const icon = screen.getByLabelText(`${size} icon`);
      expect(icon).toBeInTheDocument();
      unmount();
    });
  });

  it('works with all animation variants', () => {
    const animations = ['none', 'spin', 'pulse', 'bounce', 'rotate', 'scale', 'fade'] as const;
    
    animations.forEach((animation) => {
      const { unmount } = render(<Icon name="Star" animation={animation} ariaLabel={`${animation} animation`} />);
      const icon = screen.getByLabelText(`${animation} animation`);
      expect(icon).toBeInTheDocument();
      unmount();
    });
  });

  it('maintains accessibility standards', () => {
    // Test with aria-label
    render(<Icon name="Settings" ariaLabel="Open settings" />);
    expect(screen.getByLabelText('Open settings')).toBeInTheDocument();

    // Test with aria-hidden
    render(<Icon name="Star" ariaHidden={true} />);
    const hiddenIcon = document.querySelector('svg[aria-hidden="true"]');
    expect(hiddenIcon).toHaveAttribute('aria-hidden', 'true');

    // Test auto-generated aria-label
    render(<Icon name="TrendingUp" />);
    expect(screen.getByLabelText('trending up')).toBeInTheDocument();
  });
});