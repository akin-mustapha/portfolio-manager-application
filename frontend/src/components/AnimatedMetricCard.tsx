import React, { useEffect, useState } from 'react';
import { motion, useAnimation, useInView } from 'framer-motion';
import { Icon } from './icons';
import { 
  springTransition, 
  smoothTransition, 
  hoverVariants, 
  tapVariants,
  AnimationStyle,
  getAnimationVariants,
  getTransition
} from '../utils/animations';

interface TrendData {
  value: number;
  isPositive: boolean;
  prefix?: string;
  suffix?: string;
}

interface AnimatedMetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  loading?: boolean;
  trend?: TrendData;
  icon?: string | React.ReactNode;
  animationDelay?: number;
  animationStyle?: AnimationStyle;
  gradient?: boolean;
  hoverEffect?: boolean;
  className?: string;
  onClick?: () => void;
}

// Number animation hook for smooth value transitions
const useNumberAnimation = (targetValue: number, duration: number = 1) => {
  const [displayValue, setDisplayValue] = useState(0);
  const controls = useAnimation();

  useEffect(() => {
    const startValue = displayValue;
    const difference = targetValue - startValue;
    
    if (difference === 0) return;

    let startTime: number;
    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / (duration * 1000), 1);
      
      // Easing function for smooth animation
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const currentValue = startValue + (difference * easeOut);
      
      setDisplayValue(currentValue);
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };
    
    requestAnimationFrame(animate);
  }, [targetValue, duration, displayValue]);

  return displayValue;
};

// Shimmer loading skeleton component
const ShimmerSkeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`relative overflow-hidden bg-gray-200 rounded ${className}`}>
    <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-white/60 to-transparent" />
  </div>
);

const AnimatedMetricCard: React.FC<AnimatedMetricCardProps> = ({
  title,
  value,
  subtitle,
  loading = false,
  trend,
  icon,
  animationDelay = 0,
  animationStyle = 'from-bottom',
  gradient = false,
  hoverEffect = true,
  className = '',
  onClick
}) => {
  const ref = React.useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });
  const controls = useAnimation();

  // Extract numeric value for animation
  const numericValue = typeof value === 'number' ? value : parseFloat(value.toString().replace(/[^0-9.-]/g, '')) || 0;
  const animatedValue = useNumberAnimation(isInView ? numericValue : 0, 1.2);

  // Format the animated value back to string with original formatting
  const formatAnimatedValue = (animatedVal: number): string => {
    if (typeof value === 'string' && value.includes('%')) {
      return `${animatedVal.toFixed(2)}%`;
    }
    if (typeof value === 'string' && value.includes('£')) {
      return `£${Math.round(animatedVal).toLocaleString()}`;
    }
    if (typeof value === 'string' && value.includes('$')) {
      return `$${Math.round(animatedVal).toLocaleString()}`;
    }
    return Math.round(animatedVal).toLocaleString();
  };

  const formatTrendValue = (trend: TrendData) => {
    const prefix = trend.prefix || '';
    const suffix = trend.suffix || '';
    const formattedValue = Math.abs(trend.value).toLocaleString();
    return `${prefix}${formattedValue}${suffix}`;
  };

  useEffect(() => {
    if (isInView) {
      controls.start('animate');
    }
  }, [isInView, controls]);

  const variants = getAnimationVariants(animationStyle);
  const transition = {
    ...getTransition(animationStyle),
    delay: animationDelay,
  };

  // Base card classes with modern styling - consistent dimensions
  const baseCardClasses = `
    relative overflow-hidden rounded-xl p-6 
    transition-all duration-300 ease-smooth
    min-h-[140px] h-full flex flex-col justify-between
    bg-white/80 backdrop-blur-sm
    border border-gray-200
    shadow-sm hover:shadow-md
    ${hoverEffect ? 'hover:scale-[1.02] hover:-translate-y-1' : ''}
    ${onClick ? 'cursor-pointer' : ''}
    ${className}
  `;

  if (loading) {
    return (
      <motion.div
        ref={ref}
        className={baseCardClasses}
        initial="initial"
        animate={controls}
        variants={variants}
        transition={transition}
      >
        <div className="space-y-4">
          {/* Title skeleton */}
          <div className="flex items-center justify-between">
            <ShimmerSkeleton className="h-4 w-24" />
            <ShimmerSkeleton className="h-6 w-6 rounded-full" />
          </div>
          
          {/* Value skeleton */}
          <ShimmerSkeleton className="h-8 w-32" />
          
          {/* Trend skeleton */}
          <div className="flex items-center space-x-2">
            <ShimmerSkeleton className="h-4 w-4 rounded" />
            <ShimmerSkeleton className="h-4 w-16" />
          </div>
          
          {/* Subtitle skeleton */}
          <ShimmerSkeleton className="h-3 w-20" />
        </div>

        {/* Animated background shimmer */}
        <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-white/10 to-transparent" />
      </motion.div>
    );
  }

  return (
    <motion.div
      ref={ref}
      className={baseCardClasses}
      initial="initial"
      animate={controls}
      variants={variants}
      transition={transition}
      whileHover={hoverEffect ? hoverVariants.cardHover : undefined}
      whileTap={onClick ? tapVariants.cardTap : undefined}
      onClick={onClick}
    >
      {/* Gradient overlay for enhanced visual depth */}
      {gradient && (
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent pointer-events-none" />
      )}

      {/* Header with title and icon */}
      <div className="flex items-center justify-between mb-3">
        <motion.h3 
          className="text-sm font-medium text-gray-600 uppercase tracking-wide"
          initial={{ opacity: 0 }}
          animate={{ opacity: isInView ? 1 : 0 }}
          transition={{ delay: animationDelay + 0.2, duration: 0.5 }}
        >
          {title}
        </motion.h3>
        
        {icon && (
          <motion.div 
            className="text-gray-400"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ 
              opacity: isInView ? 1 : 0, 
              scale: isInView ? 1 : 0.8 
            }}
            transition={{ delay: animationDelay + 0.3, duration: 0.4 }}
            whileHover={hoverVariants.iconHover}
          >
            {typeof icon === 'string' ? (
              <span className="text-2xl">{icon}</span>
            ) : (
              icon
            )}
          </motion.div>
        )}
      </div>
      
      {/* Main value with number animation */}
      <div className="flex items-baseline space-x-3 mb-2">
        <motion.p 
          className="text-3xl font-bold text-gray-900"
          initial={{ opacity: 0, y: 20 }}
          animate={{ 
            opacity: isInView ? 1 : 0, 
            y: isInView ? 0 : 20 
          }}
          transition={{ delay: animationDelay + 0.4, duration: 0.6 }}
        >
          {isInView && !isNaN(numericValue) ? formatAnimatedValue(animatedValue) : value}
        </motion.p>
        
        {/* Trend indicator with animation */}
        {trend && (
          <motion.div 
            className={`flex items-center text-sm font-medium ${
              trend.isPositive 
                ? 'text-success-600 dark:text-success-400' 
                : 'text-danger-600 dark:text-danger-400'
            }`}
            initial={{ opacity: 0, x: -10 }}
            animate={{ 
              opacity: isInView ? 1 : 0, 
              x: isInView ? 0 : -10 
            }}
            transition={{ delay: animationDelay + 0.6, duration: 0.4 }}
          >
            <motion.span 
              className="mr-1"
              whileHover={{ scale: 1.2 }}
              transition={springTransition}
            >
              <Icon 
                name={trend.isPositive ? 'TrendingUp' : 'TrendingDown'} 
                size="sm" 
              />
            </motion.span>
            {formatTrendValue(trend)}
          </motion.div>
        )}
      </div>
      
      {/* Subtitle */}
      {subtitle && (
        <motion.p 
          className="text-sm text-gray-500"
          initial={{ opacity: 0 }}
          animate={{ opacity: isInView ? 1 : 0 }}
          transition={{ delay: animationDelay + 0.7, duration: 0.4 }}
        >
          {subtitle}
        </motion.p>
      )}

      {/* Hover glow effect */}
      {hoverEffect && (
        <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-primary-500/0 via-primary-500/5 to-primary-500/0 opacity-0 transition-opacity duration-300 group-hover:opacity-100 pointer-events-none" />
      )}
    </motion.div>
  );
};

export default AnimatedMetricCard;