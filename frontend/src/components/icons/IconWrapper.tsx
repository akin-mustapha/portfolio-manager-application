import React from 'react';
import { motion, MotionProps } from 'framer-motion';
import { LucideIcon } from 'lucide-react';
import { cn } from '../../utils/ui';

export type IconSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
export type IconVariant = 'default' | 'hover' | 'active' | 'disabled';
export type IconAnimation = 'none' | 'spin' | 'pulse' | 'bounce' | 'rotate' | 'scale' | 'fade';

interface IconWrapperProps {
  icon: LucideIcon;
  size?: IconSize;
  variant?: IconVariant;
  animation?: IconAnimation;
  className?: string;
  ariaLabel?: string;
  ariaHidden?: boolean;
  onClick?: () => void;
  disabled?: boolean;
  children?: never;
}

const sizeClasses: Record<IconSize, string> = {
  xs: 'w-3 h-3',
  sm: 'w-4 h-4',
  md: 'w-5 h-5',
  lg: 'w-6 h-6',
  xl: 'w-8 h-8',
  '2xl': 'w-10 h-10',
};

const variantClasses: Record<IconVariant, string> = {
  default: 'text-current',
  hover: 'text-current hover:text-primary transition-colors duration-200',
  active: 'text-primary',
  disabled: 'text-neutral-400 cursor-not-allowed opacity-50',
};

const animationVariants = {
  none: {},
  spin: {
    animate: { rotate: 360 },
    transition: { duration: 1, repeat: Infinity, ease: 'linear' },
  },
  pulse: {
    animate: { scale: [1, 1.1, 1] },
    transition: { duration: 1, repeat: Infinity, ease: 'easeInOut' },
  },
  bounce: {
    animate: { y: [0, -4, 0] },
    transition: { duration: 0.6, repeat: Infinity, ease: 'easeInOut' },
  },
  rotate: {
    whileHover: { rotate: 5 },
    transition: { type: 'spring', stiffness: 300, damping: 20 },
  },
  scale: {
    whileHover: { scale: 1.1 },
    whileTap: { scale: 0.95 },
    transition: { type: 'spring', stiffness: 300, damping: 20 },
  },
  fade: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    transition: { duration: 0.3 },
  },
};

export const IconWrapper: React.FC<IconWrapperProps> = ({
  icon: Icon,
  size = 'md',
  variant = 'default',
  animation = 'none',
  className,
  ariaLabel,
  ariaHidden = false,
  onClick,
  disabled = false,
  ...props
}) => {
  const finalVariant = disabled ? 'disabled' : variant;
  const animationProps = animationVariants[animation] as MotionProps;
  
  const iconClasses = cn(
    sizeClasses[size],
    variantClasses[finalVariant],
    onClick && !disabled && 'cursor-pointer',
    className
  );

  // Check if we're in a test environment
  const isTestEnvironment = process.env.NODE_ENV === 'test' || 
    (typeof window !== 'undefined' && window.location?.href?.includes('test'));

  // Use motion for animations when not in test environment and animation is specified
  if (animation !== 'none' && !isTestEnvironment) {
    try {
      const MotionIcon = motion(Icon);
      return (
        <MotionIcon
          className={iconClasses}
          aria-label={ariaLabel}
          aria-hidden={ariaHidden}
          onClick={disabled ? undefined : onClick}
          {...animationProps}
          {...props}
        />
      );
    } catch (error) {
      // Fallback to regular icon if motion fails
      console.warn('Framer Motion animation failed, falling back to static icon:', error);
    }
  }

  // Fallback to regular icon for tests and when animations are disabled
  return (
    <Icon
      className={iconClasses}
      aria-label={ariaLabel}
      aria-hidden={ariaHidden}
      onClick={disabled ? undefined : onClick}
      {...props}
    />
  );
};

export default IconWrapper;