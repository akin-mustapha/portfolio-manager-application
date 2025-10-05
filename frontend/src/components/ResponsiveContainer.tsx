import React from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import { 
  springTransition, 
  smoothTransition, 
  hoverVariants, 
  tapVariants,
  AnimationStyle,
  getAnimationVariants,
  getTransition
} from '../utils/animations';

interface ResponsiveContainerProps {
  children: React.ReactNode;
  variant?: 'card' | 'section' | 'panel' | 'modal' | 'sidebar';
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  gradient?: boolean;
  glass?: boolean;
  shadow?: 'none' | 'soft' | 'medium' | 'strong';
  border?: boolean;
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'xl' | 'full';
  hoverEffect?: boolean;
  clickable?: boolean;
  animationStyle?: AnimationStyle;
  animationDelay?: number;
  className?: string;
  onClick?: () => void;
  onHover?: () => void;
}

const ResponsiveContainer: React.FC<ResponsiveContainerProps> = ({
  children,
  variant = 'card',
  size = 'md',
  padding = 'md',
  gradient = false,
  glass = true,
  shadow = 'soft',
  border = true,
  rounded = 'xl',
  hoverEffect = true,
  clickable = false,
  animationStyle = 'from-bottom',
  animationDelay = 0,
  className = '',
  onClick,
  onHover,
}) => {
  const shouldReduceMotion = useReducedMotion();

  // Base styling classes
  const getVariantClasses = () => {
    switch (variant) {
      case 'section':
        return 'w-full';
      case 'panel':
        return 'w-full max-w-none';
      case 'modal':
        return 'w-full max-w-2xl mx-auto';
      case 'sidebar':
        return 'h-full w-full';
      case 'card':
      default:
        return 'w-full';
    }
  };

  const getSizeClasses = () => {
    if (variant === 'modal') {
      switch (size) {
        case 'sm': return 'max-w-md';
        case 'md': return 'max-w-2xl';
        case 'lg': return 'max-w-4xl';
        case 'xl': return 'max-w-6xl';
        case 'full': return 'max-w-full';
        default: return 'max-w-2xl';
      }
    }
    return '';
  };

  const getPaddingClasses = () => {
    switch (padding) {
      case 'none': return 'p-0';
      case 'sm': return 'p-3';
      case 'md': return 'p-6';
      case 'lg': return 'p-8';
      case 'xl': return 'p-12';
      default: return 'p-6';
    }
  };

  const getShadowClasses = () => {
    switch (shadow) {
      case 'none': return '';
      case 'soft': return 'shadow-soft';
      case 'medium': return 'shadow-medium';
      case 'strong': return 'shadow-strong';
      default: return 'shadow-soft';
    }
  };

  const getRoundedClasses = () => {
    switch (rounded) {
      case 'none': return '';
      case 'sm': return 'rounded-sm';
      case 'md': return 'rounded-md';
      case 'lg': return 'rounded-lg';
      case 'xl': return 'rounded-xl';
      case 'full': return 'rounded-full';
      default: return 'rounded-xl';
    }
  };

  // Background and glass effect classes
  const getBackgroundClasses = () => {
    let classes = '';
    
    if (glass) {
      classes += gradient 
        ? 'bg-gradient-to-br from-white/80 to-white/70 backdrop-blur-sm '
        : 'bg-white/80 backdrop-blur-sm ';
    } else {
      classes += gradient
        ? 'bg-gradient-to-br from-white to-gray-50 '
        : 'bg-white ';
    }

    if (border) {
      classes += 'border border-gray-200 ';
    }

    return classes;
  };

  // Interaction classes
  const getInteractionClasses = () => {
    let classes = 'transition-all duration-300 ease-smooth ';
    
    if (hoverEffect && !shouldReduceMotion) {
      classes += 'hover:shadow-medium hover:scale-[1.01] hover:-translate-y-0.5 ';
    }
    
    if (clickable || onClick) {
      classes += 'cursor-pointer active:scale-[0.99] ';
    }

    return classes;
  };

  // Combine all classes
  const containerClasses = `
    relative overflow-hidden
    ${getVariantClasses()}
    ${getSizeClasses()}
    ${getPaddingClasses()}
    ${getBackgroundClasses()}
    ${getShadowClasses()}
    ${getRoundedClasses()}
    ${getInteractionClasses()}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  // Animation variants
  const variants = shouldReduceMotion ? {} : getAnimationVariants(animationStyle);
  const transition = shouldReduceMotion ? {} : {
    ...getTransition(animationStyle),
    delay: animationDelay,
  };

  // Hover and tap variants (disabled if reduced motion is preferred)
  const hoverVariant = shouldReduceMotion || !hoverEffect ? undefined : hoverVariants.subtleHover;
  const tapVariant = shouldReduceMotion || !clickable ? undefined : tapVariants.cardTap;

  return (
    <motion.div
      className={containerClasses}
      variants={shouldReduceMotion ? undefined : variants}
      initial={shouldReduceMotion ? undefined : "initial"}
      animate={shouldReduceMotion ? undefined : "animate"}
      exit={shouldReduceMotion ? undefined : "exit"}
      transition={shouldReduceMotion ? undefined : transition}
      whileHover={hoverVariant}
      whileTap={tapVariant}
      onClick={onClick}
      onHoverStart={onHover}
    >
      {/* Gradient overlay for enhanced visual depth */}
      {gradient && (
        <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 to-transparent pointer-events-none" />
      )}

      {/* Glass reflection effect */}
      {glass && (
        <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent pointer-events-none" />
      )}

      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>

      {/* Hover glow effect */}
      {hoverEffect && !shouldReduceMotion && (
        <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-primary-500/0 via-primary-500/5 to-primary-500/0 opacity-0 transition-opacity duration-300 group-hover:opacity-100 pointer-events-none" />
      )}

      {/* Border beam effect for special emphasis */}
      {clickable && (
        <div className="absolute inset-0 rounded-xl opacity-0 transition-opacity duration-300 hover:opacity-100 pointer-events-none">
          <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-transparent via-primary-500/20 to-transparent animate-border-beam" />
        </div>
      )}
    </motion.div>
  );
};

export default ResponsiveContainer;