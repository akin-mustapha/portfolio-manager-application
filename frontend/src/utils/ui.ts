import { clsx, type ClassValue } from 'clsx';

// Utility function to combine class names (similar to cn utility)
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

// Glass morphism utility classes
export const glassStyles = {
  light: 'bg-white/10 backdrop-blur-md border border-white/20',
  medium: 'bg-white/20 backdrop-blur-lg border border-white/30',
  dark: 'bg-black/10 backdrop-blur-md border border-black/20',
  darker: 'bg-black/20 backdrop-blur-lg border border-black/30',
  card: 'bg-white/5 backdrop-blur-xl border border-white/10 shadow-glass',
  modal: 'bg-white/10 backdrop-blur-2xl border border-white/20 shadow-glass',
} as const;

// Gradient utility classes
export const gradientStyles = {
  primary: 'bg-gradient-to-br from-primary-500/30 to-primary-600',
  success: 'bg-gradient-to-br from-success-500/30 to-success-600',
  danger: 'bg-gradient-to-br from-danger-500/30 to-danger-600',
  glass: 'bg-glass-gradient',
  radial: 'bg-gradient-radial from-primary-500/20 via-transparent to-transparent',
  conic: 'bg-gradient-conic from-primary-500 via-purple-500 to-primary-500',
} as const;

// Shadow utility classes for depth
export const shadowStyles = {
  soft: 'shadow-soft',
  medium: 'shadow-medium',
  strong: 'shadow-strong',
  glass: 'shadow-glass shadow-glass-inset',
  none: 'shadow-none',
} as const;

// Hover state utility classes
export const hoverStyles = {
  card: 'hover:scale-[1.02] hover:-translate-y-0.5 hover:shadow-medium transition-all duration-300 ease-spring',
  button: 'hover:scale-105 hover:shadow-medium transition-all duration-200 ease-bounce-in',
  icon: 'hover:scale-110 hover:rotate-3 transition-all duration-200 ease-spring',
  subtle: 'hover:scale-[1.01] hover:brightness-110 transition-all duration-200 ease-smooth',
  glow: 'hover:shadow-lg hover:shadow-primary-500/25 transition-all duration-300',
  lift: 'hover:-translate-y-1 hover:shadow-strong transition-all duration-300 ease-spring',
} as const;

// Focus state utility classes
export const focusStyles = {
  ring: 'focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:ring-offset-2',
  glow: 'focus:outline-none focus:shadow-lg focus:shadow-primary-500/25',
  subtle: 'focus:outline-none focus:ring-1 focus:ring-primary-400/30',
} as const;

// Active/pressed state utility classes
export const activeStyles = {
  scale: 'active:scale-95 transition-transform duration-100',
  press: 'active:scale-98 active:brightness-95 transition-all duration-100',
  bounce: 'active:scale-90 transition-transform duration-150 ease-bounce-in',
} as const;

// Loading state utility classes
export const loadingStyles = {
  shimmer: 'animate-shimmer bg-gradient-to-r from-transparent via-white/10 to-transparent',
  pulse: 'animate-pulse bg-gray-200 dark:bg-gray-700',
  spin: 'animate-spin',
  bounce: 'animate-bounce-subtle',
  float: 'animate-float',
} as const;

// Responsive breakpoint utilities
export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

// Color system utilities
export const colorSystem = {
  primary: {
    gradient: 'from-primary-500/30 to-primary-600',
    background: 'bg-primary-500/10',
    text: 'text-primary-600 dark:text-primary-400',
    border: 'border-primary-500/20',
    hover: 'hover:bg-primary-500/20',
  },
  success: {
    gradient: 'from-success-500/30 to-success-600',
    background: 'bg-success-500/10',
    text: 'text-success-600 dark:text-success-400',
    border: 'border-success-500/20',
    hover: 'hover:bg-success-500/20',
  },
  danger: {
    gradient: 'from-danger-500/30 to-danger-600',
    background: 'bg-danger-500/10',
    text: 'text-danger-600 dark:text-danger-400',
    border: 'border-danger-500/20',
    hover: 'hover:bg-danger-500/20',
  },
  neutral: {
    glass: 'bg-neutral-900/50 dark:bg-neutral-100/50',
    backdrop: 'bg-black/50',
    border: 'border-neutral-200 dark:border-neutral-800',
    text: 'text-neutral-700 dark:text-neutral-300',
  },
} as const;

// Interactive element utilities
export const interactiveStyles = {
  hover: 'group-hover:brightness-[0.8] transition-all duration-200',
  focus: 'focus:ring-2 focus:ring-primary-500/50 focus:outline-none',
  active: 'active:scale-95 transition-transform duration-100',
  disabled: 'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
} as const;

// Utility function to create consistent card styles
export const createCardStyles = (variant: 'glass' | 'solid' | 'gradient' = 'glass') => {
  const baseStyles = 'rounded-xl p-6 transition-all duration-300';
  
  switch (variant) {
    case 'glass':
      return cn(baseStyles, glassStyles.card, hoverStyles.card);
    case 'solid':
      return cn(baseStyles, 'bg-white dark:bg-gray-800 shadow-medium', hoverStyles.card);
    case 'gradient':
      return cn(baseStyles, gradientStyles.glass, shadowStyles.glass, hoverStyles.card);
    default:
      return cn(baseStyles, glassStyles.card, hoverStyles.card);
  }
};

// Utility function to create consistent button styles
export const createButtonStyles = (
  variant: 'primary' | 'secondary' | 'ghost' | 'danger' = 'primary',
  size: 'sm' | 'md' | 'lg' = 'md'
) => {
  const baseStyles = 'inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200';
  
  const sizeStyles = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  
  const variantStyles = {
    primary: cn(
      'bg-primary-600 text-white shadow-medium',
      hoverStyles.button,
      'hover:bg-primary-700',
      focusStyles.ring,
      activeStyles.scale
    ),
    secondary: cn(
      'bg-white/10 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600',
      hoverStyles.subtle,
      focusStyles.ring,
      activeStyles.scale
    ),
    ghost: cn(
      'text-gray-700 dark:text-gray-300',
      hoverStyles.subtle,
      'hover:bg-gray-100 dark:hover:bg-gray-800',
      focusStyles.subtle,
      activeStyles.scale
    ),
    danger: cn(
      'bg-danger-600 text-white shadow-medium',
      hoverStyles.button,
      'hover:bg-danger-700',
      focusStyles.ring,
      activeStyles.scale
    ),
  };
  
  return cn(baseStyles, sizeStyles[size], variantStyles[variant]);
};

// Utility function for consistent loading skeleton
export const createSkeletonStyles = (className?: string) => {
  return cn(
    'relative overflow-hidden rounded-md bg-gray-200 dark:bg-gray-700',
    'before:absolute before:inset-0 before:-translate-x-full',
    'before:bg-gradient-to-r before:from-transparent before:via-white/20 before:to-transparent',
    'before:animate-shimmer',
    className
  );
};

// Utility function to handle reduced motion preferences
export const getMotionPreference = () => {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

// Utility function to create responsive animation delays
export const createStaggerDelay = (index: number, baseDelay: number = 0.1) => {
  return index * baseDelay;
};