import { MotionProps } from 'framer-motion';
import { 
  AnimationStyle, 
  getAnimationVariants, 
  getTransition,
  springTransition,
  smoothTransition,
  bounceTransition,
  hoverVariants,
  tapVariants
} from './animations';

// Motion configuration interface
export interface MotionConfig {
  initial?: MotionProps['initial'];
  animate?: MotionProps['animate'];
  exit?: MotionProps['exit'];
  transition?: MotionProps['transition'];
  whileHover?: MotionProps['whileHover'];
  whileTap?: MotionProps['whileTap'];
}

// Create motion configuration from animation style
export const createMotionConfig = (
  style: AnimationStyle,
  options?: {
    delay?: number;
    duration?: number;
    stagger?: boolean;
    hover?: keyof typeof hoverVariants;
    tap?: keyof typeof tapVariants;
  }
): MotionConfig => {
  const variants = getAnimationVariants(style);
  const transition = getTransition(style);
  
  const config: MotionConfig = {
    initial: variants.initial as MotionProps['initial'],
    animate: variants.animate as MotionProps['animate'],
    exit: variants.exit as MotionProps['exit'],
    transition: {
      ...transition,
      delay: options?.delay || 0,
      ...(options?.duration && { duration: options.duration }),
    },
  };
  
  // Add hover animation if specified
  if (options?.hover) {
    config.whileHover = hoverVariants[options.hover] as MotionProps['whileHover'];
  }
  
  // Add tap animation if specified
  if (options?.tap) {
    config.whileTap = tapVariants[options.tap] as MotionProps['whileTap'];
  }
  
  return config;
};

// Pre-configured motion configs for common use cases
export const motionConfigs = {
  // Card animations
  card: createMotionConfig('from-bottom', { 
    hover: 'cardHover', 
    tap: 'cardTap' 
  }),
  
  // Button animations
  button: createMotionConfig('scale', { 
    hover: 'buttonHover', 
    tap: 'buttonTap' 
  }),
  
  // Icon animations
  icon: createMotionConfig('fade', { 
    hover: 'iconHover', 
    tap: 'iconTap' 
  }),
  
  // Modal animations
  modal: createMotionConfig('from-center', { duration: 0.3 }),
  
  // Page transitions
  page: createMotionConfig('from-right', { duration: 0.4 }),
  
  // List item animations
  listItem: createMotionConfig('from-bottom', { duration: 0.2 }),
  
  // Metric card with number animation
  metric: createMotionConfig('from-bottom', { 
    delay: 0.1,
    hover: 'subtleHover' 
  }),
  
  // Chart animations
  chart: createMotionConfig('scale', { 
    duration: 0.6,
    hover: 'subtleHover' 
  }),
  
  // Sidebar/drawer animations
  drawer: createMotionConfig('from-left', { duration: 0.3 }),
  
  // Tooltip animations
  tooltip: createMotionConfig('scale', { duration: 0.15 }),
  
  // Loading animations
  loading: createMotionConfig('fade', { duration: 0.2 }),
} as const;

// Layout animation configurations
export const layoutAnimations = {
  // Shared layout animations for smooth transitions
  sharedLayout: {
    layoutId: 'shared-element',
    transition: springTransition,
  },
  
  // Page layout animations
  pageLayout: {
    initial: { opacity: 0, x: 20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 },
    transition: smoothTransition,
  },
  
  // Modal backdrop
  backdrop: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.2 },
  },
} as const;

// Gesture configurations
export const gestureConfigs = {
  // Drag configurations
  drag: {
    drag: true,
    dragConstraints: { left: 0, right: 0, top: 0, bottom: 0 },
    dragElastic: 0.1,
    whileDrag: { scale: 1.05 },
  },
  
  // Swipe configurations
  swipe: {
    drag: 'x' as const,
    dragConstraints: { left: 0, right: 0 },
    dragElastic: 0.2,
  },
  
  // Pan configurations for charts
  pan: {
    drag: true,
    dragMomentum: false,
    dragElastic: 0,
  },
} as const;

// Accessibility configurations
export const a11yConfigs = {
  // Reduced motion configuration
  reducedMotion: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.1 },
  },
  
  // Focus configurations
  focus: {
    whileFocus: { 
      scale: 1.02,
      transition: { duration: 0.1 }
    },
  },
} as const;

// Utility function to get motion config with reduced motion support
export const getMotionConfig = (
  configName: keyof typeof motionConfigs,
  respectReducedMotion: boolean = true
): MotionConfig => {
  if (respectReducedMotion && typeof window !== 'undefined') {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
      return a11yConfigs.reducedMotion;
    }
  }
  
  return motionConfigs[configName];
};





// Export commonly used motion props
export const commonMotionProps = {
  // Standard fade in
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
  },
  
  // Standard slide up
  slideUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
  },
  
  // Standard scale
  scale: {
    initial: { opacity: 0, scale: 0.9 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.95 },
  },
} as const;