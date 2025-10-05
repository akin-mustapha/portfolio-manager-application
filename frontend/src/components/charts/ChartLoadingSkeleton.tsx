import React from 'react';
import { motion } from 'framer-motion';

interface ChartLoadingSkeletonProps {
  height?: number;
  type?: 'line' | 'scatter' | 'timeseries';
  showLegend?: boolean;
}

const ChartLoadingSkeleton: React.FC<ChartLoadingSkeletonProps> = ({
  height = 300,
  type = 'line',
  showLegend = false
}) => {
  const shimmerVariants = {
    initial: { opacity: 0.3 },
    animate: { 
      opacity: [0.3, 0.8, 0.3],
    }
  };

  const shimmerTransition = {
    duration: 1.5,
    repeat: Infinity,
    ease: "easeInOut" as const
  };

  const renderLineChart = () => (
    <div className="space-y-4">
      {/* Chart area */}
      <div className="relative" style={{ height }}>
        <div className="absolute inset-0 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg border border-gray-200">
          {/* Y-axis labels */}
          <div className="absolute left-2 top-4 space-y-8">
            {[...Array(5)].map((_, i) => (
              <motion.div
                key={i}
                variants={shimmerVariants}
                initial="initial"
                animate="animate"
                transition={{ ...shimmerTransition, delay: i * 0.1 }}
                className="w-8 h-3 bg-gray-300 rounded"
              />
            ))}
          </div>
          
          {/* Chart lines */}
          <div className="absolute inset-8">
            <svg width="100%" height="100%" className="overflow-visible">
              {/* Grid lines */}
              {[...Array(5)].map((_, i) => (
                <motion.line
                  key={`grid-${i}`}
                  x1="0"
                  y1={`${(i + 1) * 20}%`}
                  x2="100%"
                  y2={`${(i + 1) * 20}%`}
                  stroke="#e5e7eb"
                  strokeWidth="1"
                  strokeDasharray="2,2"
                  variants={shimmerVariants}
                  initial="initial"
                  animate="animate"
                  transition={{ ...shimmerTransition, delay: i * 0.05 }}
                />
              ))}
              
              {/* Animated line path */}
              <motion.path
                d="M 0,80% Q 25%,60% 50%,40% T 100%,20%"
                fill="none"
                stroke="#3B82F6"
                strokeWidth="2"
                strokeOpacity="0.3"
                variants={shimmerVariants}
                initial="initial"
                animate="animate"
                transition={shimmerTransition}
              />
              
              {/* Data points */}
              {[...Array(6)].map((_, i) => (
                <motion.circle
                  key={`point-${i}`}
                  cx={`${i * 20}%`}
                  cy={`${60 - i * 8}%`}
                  r="3"
                  fill="#3B82F6"
                  fillOpacity="0.3"
                  variants={shimmerVariants}
                  initial="initial"
                  animate="animate"
                  transition={{ ...shimmerTransition, delay: i * 0.1 }}
                />
              ))}
            </svg>
          </div>
          
          {/* X-axis labels */}
          <div className="absolute bottom-2 left-8 right-8 flex justify-between">
            {[...Array(6)].map((_, i) => (
              <motion.div
                key={i}
                variants={shimmerVariants}
                initial="initial"
                animate="animate"
                transition={{ ...shimmerTransition, delay: i * 0.1 }}
                className="w-12 h-3 bg-gray-300 rounded"
              />
            ))}
          </div>
        </div>
      </div>
      
      {/* Legend */}
      {showLegend && (
        <div className="flex justify-center space-x-6">
          {[...Array(3)].map((_, i) => (
            <motion.div
              key={i}
              variants={shimmerVariants}
              initial="initial"
              animate="animate"
              transition={{ ...shimmerTransition, delay: i * 0.2 }}
              className="flex items-center space-x-2"
            >
              <div className="w-4 h-4 bg-gray-300 rounded-full" />
              <div className="w-16 h-3 bg-gray-300 rounded" />
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );

  const renderScatterChart = () => (
    <div className="space-y-4">
      <div className="relative" style={{ height }}>
        <div className="absolute inset-0 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg border border-gray-200">
          {/* Axes */}
          <div className="absolute inset-8">
            <svg width="100%" height="100%">
              {/* Grid */}
              {[...Array(5)].map((_, i) => (
                <g key={i}>
                  <motion.line
                    x1="0"
                    y1={`${i * 25}%`}
                    x2="100%"
                    y2={`${i * 25}%`}
                    stroke="#e5e7eb"
                    strokeWidth="1"
                    strokeDasharray="2,2"
                    variants={shimmerVariants}
                    initial="initial"
                    animate="animate"
                    transition={{ ...shimmerTransition, delay: i * 0.05 }}
                  />
                  <motion.line
                    x1={`${i * 25}%`}
                    y1="0"
                    x2={`${i * 25}%`}
                    y2="100%"
                    stroke="#e5e7eb"
                    strokeWidth="1"
                    strokeDasharray="2,2"
                    variants={shimmerVariants}
                    initial="initial"
                    animate="animate"
                    transition={{ ...shimmerTransition, delay: i * 0.05 }}
                  />
                </g>
              ))}
              
              {/* Scatter points */}
              {[...Array(12)].map((_, i) => (
                <motion.circle
                  key={i}
                  cx={`${Math.random() * 80 + 10}%`}
                  cy={`${Math.random() * 80 + 10}%`}
                  r={Math.random() * 4 + 2}
                  fill="#3B82F6"
                  fillOpacity="0.3"
                  variants={shimmerVariants}
                  initial="initial"
                  animate="animate"
                  transition={{ ...shimmerTransition, delay: i * 0.1 }}
                />
              ))}
            </svg>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="w-full">
      {type === 'scatter' ? renderScatterChart() : renderLineChart()}
    </div>
  );
};

export default ChartLoadingSkeleton;