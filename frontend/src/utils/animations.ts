import { Variants, Transition } from 'framer-motion';

// Animation styles enum for consistent usage
export type AnimationStyle = 
  | 'from-bottom' 
  | 'from-center' 
  | 'from-top' 
  | 'from-left' 
  | 'from-right' 
  | 'fade'
  | 'top-in-bottom-out' 
  | 'left-in-right-out'
  | 'scale'
  | 'bounce';

// Standard spring transition configuration
export const springTransition: Transition = {
  type: 'spring',
  damping: 25,
  stiffness: 300,
  mass: 0.8,
};

// Smooth transition for subtle animations
export const smoothTransition: Transition = {
  type: 'tween',
  duration: 0.3,
  ease: [0.4, 0, 0.2, 1],
};

// Bounce transition for playful interactions
export const bounceTransition: Transition = {
  type: 'spring',
  damping: 15,
  stiffness: 400,
  mass: 0.6,
};

// Standard animation variants
export const fadeVariants: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
};

export const slideUpVariants: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
};

export const slideDownVariants: Variants = {
  initial: { opacity: 0, y: -20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 20 },
};

export const slideLeftVariants: Variants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
};

export const slideRightVariants: Variants = {
  initial: { opacity: 0, x: 20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 },
};

export const scaleVariants: Variants = {
  initial: { opacity: 0, scale: 0.9 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 },
};

export const bounceVariants: Variants = {
  initial: { opacity: 0, scale: 0.3 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.5 },
};

// Container variants for staggered animations
export const containerVariants: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
  exit: {
    transition: {
      staggerChildren: 0.05,
      staggerDirection: -1,
    },
  },
};

export const listItemVariants: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -10 },
};

// Hover animation variants
export const hoverVariants = {
  cardHover: {
    scale: 1.02,
    y: -2,
    transition: springTransition,
  },
  buttonHover: {
    scale: 1.05,
    transition: bounceTransition,
  },
  iconHover: {
    scale: 1.1,
    rotate: 5,
    transition: springTransition,
  },
  subtleHover: {
    scale: 1.01,
    transition: smoothTransition,
  },
};

// Tap animation variants
export const tapVariants = {
  cardTap: {
    scale: 0.98,
    transition: { duration: 0.1 },
  },
  buttonTap: {
    scale: 0.95,
    transition: { duration: 0.1 },
  },
  iconTap: {
    scale: 0.9,
    transition: { duration: 0.1 },
  },
};

// Function to get animation variants by style
export const getAnimationVariants = (style: AnimationStyle): Variants => {
  switch (style) {
    case 'from-bottom':
    case 'top-in-bottom-out':
      return slideUpVariants;
    case 'from-top':
      return slideDownVariants;
    case 'from-left':
    case 'left-in-right-out':
      return slideLeftVariants;
    case 'from-right':
      return slideRightVariants;
    case 'from-center':
    case 'scale':
      return scaleVariants;
    case 'bounce':
      return bounceVariants;
    case 'fade':
    default:
      return fadeVariants;
  }
};

// Function to get transition by style
export const getTransition = (style: AnimationStyle): Transition => {
  switch (style) {
    case 'bounce':
      return bounceTransition;
    case 'scale':
    case 'from-center':
      return springTransition;
    default:
      return smoothTransition;
  }
};

// Utility function to create staggered container animations
export const createStaggerContainer = (
  staggerDelay: number = 0.1,
  delayChildren: number = 0.1
): Variants => ({
  initial: {},
  animate: {
    transition: {
      staggerChildren: staggerDelay,
      delayChildren,
    },
  },
  exit: {
    transition: {
      staggerChildren: staggerDelay * 0.5,
      staggerDirection: -1,
    },
  },
});

// Utility function for number animations (for metric cards)
export const createNumberAnimation = (
  from: number,
  to: number,
  duration: number = 1
) => ({
  initial: { value: from },
  animate: { value: to },
  transition: {
    duration,
    ease: 'easeOut',
  },
});

// Stagger animation utilities
export const staggerConfigs = {
  // Container for staggered children
  container: {
    initial: {},
    animate: {
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.1,
      },
    },
    exit: {
      transition: {
        staggerChildren: 0.05,
        staggerDirection: -1,
      },
    },
  },
  
  // Fast stagger for quick animations
  fast: {
    initial: {},
    animate: {
      transition: {
        staggerChildren: 0.05,
        delayChildren: 0.05,
      },
    },
  },
  
  // Slow stagger for dramatic effect
  slow: {
    initial: {},
    animate: {
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.2,
      },
    },
  },
} as const;

// Chart-specific animation configurations
export const chartAnimations = {
  // Line chart path animation
  linePath: {
    initial: { pathLength: 0, opacity: 0 },
    animate: { pathLength: 1, opacity: 1 },
    transition: { duration: 1.5, ease: 'easeInOut' },
  },
  
  // Bar chart animation
  bar: {
    initial: { scaleY: 0, originY: 1 },
    animate: { scaleY: 1 },
    transition: springTransition,
  },
  
  // Pie chart segment animation
  pieSegment: {
    initial: { scale: 0, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    transition: { ...springTransition, delay: 0.1 },
  },
  
  // Data point animation
  dataPoint: {
    initial: { scale: 0, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    whileHover: { scale: 1.2 },
    transition: bounceTransition,
  },
} as const;