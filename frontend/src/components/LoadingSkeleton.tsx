import React from 'react';
import { motion } from 'framer-motion';
import { fadeVariants, smoothTransition } from '../utils/animations';

interface LoadingSkeletonProps {
  variant?: 'card' | 'text' | 'circle' | 'rectangle' | 'chart' | 'table' | 'dashboard';
  width?: string | number;
  height?: string | number;
  className?: string;
  animate?: boolean;
  rows?: number; // For table variant
  columns?: number; // For dashboard variant
}

interface ShimmerBaseProps {
  className?: string;
  animate?: boolean;
  style?: React.CSSProperties;
}

// Base shimmer skeleton component
const ShimmerBase: React.FC<ShimmerBaseProps> = ({ 
  className = '', 
  animate = true,
  style
}) => (
  <div className={`relative overflow-hidden bg-gray-200 dark:bg-gray-700 ${className}`} style={style}>
    {animate && (
      <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-white/60 dark:via-gray-600/60 to-transparent" />
    )}
  </div>
);

// Card skeleton with multiple elements
const CardSkeleton: React.FC<{ animate?: boolean }> = ({ animate = true }) => (
  <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border border-white/20 dark:border-gray-700/20 rounded-xl p-6 shadow-soft">
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <ShimmerBase className="h-4 w-24 rounded" animate={animate} />
        <ShimmerBase className="h-6 w-6 rounded-full" animate={animate} />
      </div>
      
      {/* Main value */}
      <ShimmerBase className="h-8 w-32 rounded" animate={animate} />
      
      {/* Trend indicator */}
      <div className="flex items-center space-x-2">
        <ShimmerBase className="h-4 w-4 rounded" animate={animate} />
        <ShimmerBase className="h-4 w-16 rounded" animate={animate} />
      </div>
      
      {/* Subtitle */}
      <ShimmerBase className="h-3 w-20 rounded" animate={animate} />
    </div>
  </div>
);

// Chart skeleton
const ChartSkeleton: React.FC<{ animate?: boolean }> = ({ animate = true }) => (
  <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border border-white/20 dark:border-gray-700/20 rounded-xl p-6 shadow-soft">
    <div className="space-y-4">
      {/* Chart title */}
      <ShimmerBase className="h-5 w-32 rounded" animate={animate} />
      
      {/* Chart area */}
      <div className="relative h-64 bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden">
        {/* Simulated chart bars */}
        <div className="absolute bottom-0 left-0 right-0 flex items-end justify-around p-4 space-x-2">
          {[...Array(8)].map((_, i) => (
            <ShimmerBase
              key={i}
              className={`w-6 rounded-t`}
              style={{ height: `${Math.random() * 60 + 20}%` }}
              animate={animate}
            />
          ))}
        </div>
        
        {/* Chart shimmer overlay */}
        {animate && (
          <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-white/20 dark:via-gray-600/20 to-transparent" />
        )}
      </div>
      
      {/* Legend */}
      <div className="flex justify-center space-x-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="flex items-center space-x-2">
            <ShimmerBase className="h-3 w-3 rounded-full" animate={animate} />
            <ShimmerBase className="h-3 w-12 rounded" animate={animate} />
          </div>
        ))}
      </div>
    </div>
  </div>
);

// Table skeleton
const TableSkeleton: React.FC<{ rows?: number; animate?: boolean }> = ({ 
  rows = 5, 
  animate = true 
}) => (
  <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border border-white/20 dark:border-gray-700/20 rounded-xl overflow-hidden shadow-soft">
    {/* Table header */}
    <div className="border-b border-gray-200 dark:border-gray-700 p-4">
      <div className="grid grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <ShimmerBase key={i} className="h-4 rounded" animate={animate} />
        ))}
      </div>
    </div>
    
    {/* Table rows */}
    <div className="divide-y divide-gray-200 dark:divide-gray-700">
      {[...Array(rows)].map((_, rowIndex) => (
        <div key={rowIndex} className="p-4">
          <div className="grid grid-cols-4 gap-4 items-center">
            <div className="flex items-center space-x-3">
              <ShimmerBase className="h-8 w-8 rounded-full" animate={animate} />
              <ShimmerBase className="h-4 w-20 rounded" animate={animate} />
            </div>
            <ShimmerBase className="h-4 w-16 rounded" animate={animate} />
            <ShimmerBase className="h-4 w-12 rounded" animate={animate} />
            <ShimmerBase className="h-4 w-14 rounded" animate={animate} />
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Dashboard skeleton with multiple cards
const DashboardSkeleton: React.FC<{ columns?: number; animate?: boolean }> = ({ 
  columns = 4, 
  animate = true 
}) => {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
  };

  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border border-white/20 dark:border-gray-700/20 rounded-xl p-6 shadow-soft">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <ShimmerBase className="h-6 w-48 rounded" animate={animate} />
            <ShimmerBase className="h-4 w-64 rounded" animate={animate} />
          </div>
          <ShimmerBase className="h-10 w-32 rounded-lg" animate={animate} />
        </div>
      </div>

      {/* Metric cards grid */}
      <div className={`grid ${gridCols[columns as keyof typeof gridCols]} gap-6`}>
        {[...Array(columns)].map((_, i) => (
          <CardSkeleton key={i} animate={animate} />
        ))}
      </div>

      {/* Charts section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartSkeleton animate={animate} />
        <TableSkeleton rows={4} animate={animate} />
      </div>
    </div>
  );
};

const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  variant = 'rectangle',
  width,
  height,
  className = '',
  animate = true,
  rows = 5,
  columns = 4,
}) => {
  const getSkeletonComponent = () => {
    switch (variant) {
      case 'card':
        return <CardSkeleton animate={animate} />;
      
      case 'chart':
        return <ChartSkeleton animate={animate} />;
      
      case 'table':
        return <TableSkeleton rows={rows} animate={animate} />;
      
      case 'dashboard':
        return <DashboardSkeleton columns={columns} animate={animate} />;
      
      case 'circle':
        return (
          <ShimmerBase 
            className={`rounded-full ${className}`}
            style={{ width, height }}
            animate={animate}
          />
        );
      
      case 'text':
        return (
          <ShimmerBase 
            className={`rounded ${className}`}
            style={{ width, height: height || '1rem' }}
            animate={animate}
          />
        );
      
      case 'rectangle':
      default:
        return (
          <ShimmerBase 
            className={`rounded ${className}`}
            style={{ width, height }}
            animate={animate}
          />
        );
    }
  };

  return (
    <motion.div
      variants={fadeVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={smoothTransition}
    >
      {getSkeletonComponent()}
    </motion.div>
  );
};

export default LoadingSkeleton;