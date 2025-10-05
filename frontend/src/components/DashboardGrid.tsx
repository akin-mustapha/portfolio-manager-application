import React from 'react';
import { motion } from 'framer-motion';
import { 
  containerVariants, 
  listItemVariants, 
  createStaggerContainer,
  AnimationStyle 
} from '../utils/animations';

interface DashboardGridProps {
  children: React.ReactNode;
  columns?: 1 | 2 | 3 | 4 | 5 | 6;
  gap?: 'sm' | 'md' | 'lg' | 'xl';
  staggerDelay?: number;
  animationStyle?: AnimationStyle;
  className?: string;
}

const DashboardGrid: React.FC<DashboardGridProps> = ({
  children,
  columns = 4,
  gap = 'md',
  staggerDelay = 0.1,
  animationStyle = 'from-bottom',
  className = ''
}) => {
  // Grid column classes
  const columnClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
    5: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5',
    6: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6',
  };

  // Gap classes
  const gapClasses = {
    sm: 'gap-3',
    md: 'gap-6',
    lg: 'gap-8',
    xl: 'gap-12',
  };

  // Create staggered container variants
  const staggerContainer = createStaggerContainer(staggerDelay, 0.1);

  return (
    <motion.div
      className={`grid ${columnClasses[columns]} ${gapClasses[gap]} ${className}`}
      variants={staggerContainer}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      {React.Children.map(children, (child, index) => (
        <motion.div
          key={index}
          variants={listItemVariants}
          custom={index}
        >
          {child}
        </motion.div>
      ))}
    </motion.div>
  );
};

export default DashboardGrid;