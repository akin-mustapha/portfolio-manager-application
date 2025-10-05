import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, useInView } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { Icon } from '../icons';
import { 
  springTransition, 
  smoothTransition,
  staggerConfigs
} from '../../utils/animations';

export interface DonutChartData {
  name: string;
  value: number;
  percentage: number;
  color?: string;
  category?: string;
  description?: string;
}

interface AnimatedDonutChartProps {
  data: DonutChartData[];
  title?: string;
  centerLabel?: string;
  centerValue?: string | number;
  loading?: boolean;
  height?: number;
  showTooltip?: boolean;
  progressiveLoading?: boolean;
  animationDelay?: number;
  onSegmentClick?: (data: DonutChartData) => void;
  className?: string;
}

// Sector-specific color palette
const SECTOR_COLORS = {
  'Technology': '#3B82F6',
  'Healthcare': '#10B981', 
  'Financial': '#F59E0B',
  'Consumer': '#EF4444',
  'Industrial': '#8B5CF6',
  'Energy': '#06B6D4',
  'Materials': '#84CC16',
  'Utilities': '#F97316',
  'Real Estate': '#EC4899',
  'Communication': '#6B7280',
  'Other': '#94A3B8'
};

const DEFAULT_COLORS = [
  '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
  '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6B7280'
];

// Progressive loading animation hook
const useProgressiveLoading = (data: DonutChartData[], enabled: boolean, delay: number = 0) => {
  const [visibleData, setVisibleData] = useState<DonutChartData[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (!enabled || data.length === 0) {
      setVisibleData(data);
      return;
    }

    setVisibleData([]);
    setCurrentIndex(0);

    const timer = setTimeout(() => {
      const interval = setInterval(() => {
        setCurrentIndex(prev => {
          const nextIndex = prev + 1;
          if (nextIndex <= data.length) {
            setVisibleData(data.slice(0, nextIndex));
          }
          
          if (nextIndex >= data.length) {
            clearInterval(interval);
          }
          
          return nextIndex;
        });
      }, 200);

      return () => clearInterval(interval);
    }, delay);

    return () => clearTimeout(timer);
  }, [data, enabled, delay]);

  return visibleData;
};

// Custom tooltip with enhanced styling
const CustomTooltip: React.FC<any> = ({ active, payload }) => {
  if (!active || !payload || !payload.length) return null;

  const data = payload[0].payload;
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, y: 10 }}
      transition={smoothTransition}
      className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-md border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-lg max-w-xs"
    >
      <div className="flex items-center space-x-2 mb-3">
        <div 
          className="w-4 h-4 rounded-full"
          style={{ backgroundColor: data.color }}
        />
        <span className="font-semibold text-gray-900 dark:text-white">
          {data.name}
        </span>
      </div>
      
      <div className="space-y-2 text-sm">
        <div className="flex justify-between items-center">
          <span className="text-gray-600 dark:text-gray-400">Value:</span>
          <span className="font-medium text-gray-900 dark:text-white">
            £{data.value.toLocaleString()}
          </span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-gray-600 dark:text-gray-400">Percentage:</span>
          <span className="font-medium text-gray-900 dark:text-white">
            {data.percentage.toFixed(1)}%
          </span>
        </div>
        
        {data.category && (
          <div className="flex justify-between items-center">
            <span className="text-gray-600 dark:text-gray-400">Category:</span>
            <span className="font-medium text-gray-900 dark:text-white">
              {data.category}
            </span>
          </div>
        )}
        
        {data.description && (
          <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
            <p className="text-gray-600 dark:text-gray-400 text-xs">
              {data.description}
            </p>
          </div>
        )}
      </div>
    </motion.div>
  );
};

// Center label component with animations
const CenterLabel: React.FC<{
  label?: string;
  value?: string | number;
  isVisible: boolean;
  delay: number;
}> = ({ label, value, isVisible, delay }) => {
  if (!label && !value) return null;

  return (
    <motion.div
      className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ 
        opacity: isVisible ? 1 : 0, 
        scale: isVisible ? 1 : 0.8 
      }}
      transition={{ delay: delay + 0.8, ...springTransition }}
    >
      {value && (
        <motion.div 
          className="text-2xl font-bold text-gray-900 dark:text-white"
          initial={{ opacity: 0, y: 10 }}
          animate={{ 
            opacity: isVisible ? 1 : 0, 
            y: isVisible ? 0 : 10 
          }}
          transition={{ delay: delay + 1, duration: 0.5 }}
        >
          {typeof value === 'number' ? value.toLocaleString() : value}
        </motion.div>
      )}
      
      {label && (
        <motion.div 
          className="text-sm text-gray-600 dark:text-gray-400 mt-1"
          initial={{ opacity: 0, y: 5 }}
          animate={{ 
            opacity: isVisible ? 1 : 0, 
            y: isVisible ? 0 : 5 
          }}
          transition={{ delay: delay + 1.2, duration: 0.4 }}
        >
          {label}
        </motion.div>
      )}
    </motion.div>
  );
};

// Loading skeleton
const DonutChartSkeleton: React.FC<{ height: number }> = ({ height }) => (
  <div className="flex items-center justify-center" style={{ height }}>
    <div className="relative">
      <div 
        className="bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse"
        style={{ 
          width: Math.min(height * 0.7, 200), 
          height: Math.min(height * 0.7, 200) 
        }}
      />
      <div 
        className="absolute bg-white dark:bg-gray-800 rounded-full"
        style={{
          width: Math.min(height * 0.35, 100),
          height: Math.min(height * 0.35, 100),
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)'
        }}
      />
    </div>
  </div>
);

const AnimatedDonutChart: React.FC<AnimatedDonutChartProps> = ({
  data,
  title,
  centerLabel,
  centerValue,
  loading = false,
  height = 300,
  showTooltip = true,
  progressiveLoading = true,
  animationDelay = 0,
  onSegmentClick,
  className = ''
}) => {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });

  // Use progressive loading if enabled
  const visibleData = useProgressiveLoading(data, progressiveLoading && isInView, animationDelay * 1000);

  // Prepare data with colors
  const chartData = visibleData.map((item, index) => ({
    ...item,
    color: item.color || 
           SECTOR_COLORS[item.category as keyof typeof SECTOR_COLORS] || 
           DEFAULT_COLORS[index % DEFAULT_COLORS.length]
  }));

  // Handle interactions
  const handleMouseEnter = (data: any, index: number) => {
    setHoveredIndex(index);
  };

  const handleMouseLeave = () => {
    setHoveredIndex(null);
  };

  const handleClick = (data: any, index: number) => {
    setActiveIndex(activeIndex === index ? null : index);
    onSegmentClick?.(data);
  };

  if (loading) {
    return (
      <motion.div
        ref={ref}
        className={`bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border border-white/20 dark:border-gray-700/20 rounded-xl p-6 shadow-soft ${className}`}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: animationDelay, ...smoothTransition }}
      >
        {title && (
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {title}
          </h3>
        )}
        <DonutChartSkeleton height={height} />
      </motion.div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <motion.div
        ref={ref}
        className={`bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border border-white/20 dark:border-gray-700/20 rounded-xl p-6 shadow-soft ${className}`}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: animationDelay, ...smoothTransition }}
      >
        {title && (
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {title}
          </h3>
        )}
        <div className="flex items-center justify-center" style={{ height }}>
          <div className="text-center">
            <div className="text-gray-400 mb-2">
              <Icon name="PieChart" size="2xl" />
            </div>
            <p className="text-gray-500 font-medium">No sector data available</p>
            <p className="text-gray-400 text-sm mt-1">
              Data will appear when portfolio is loaded
            </p>
          </div>
        </div>
      </motion.div>
    );
  }

  const outerRadius = Math.min(height * 0.35, 100);
  const innerRadius = Math.min(height * 0.2, 60);

  return (
    <motion.div
      ref={ref}
      className={`bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border border-white/20 dark:border-gray-700/20 rounded-xl p-6 shadow-soft hover:shadow-medium transition-all duration-300 ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: isInView ? 1 : 0, y: isInView ? 0 : 20 }}
      transition={{ delay: animationDelay, ...smoothTransition }}
      whileHover={{ scale: 1.01 }}
    >
      {/* Header */}
      {title && (
        <motion.h3 
          className="text-lg font-semibold text-gray-900 dark:text-white mb-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: isInView ? 1 : 0 }}
          transition={{ delay: animationDelay + 0.2, duration: 0.5 }}
        >
          {title}
        </motion.h3>
      )}

      {/* Chart Container */}
      <motion.div
        className="relative"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ 
          opacity: isInView ? 1 : 0, 
          scale: isInView ? 1 : 0.9 
        }}
        transition={{ delay: animationDelay + 0.3, ...springTransition }}
        style={{ height }}
      >
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              outerRadius={outerRadius}
              innerRadius={innerRadius}
              paddingAngle={1}
              dataKey="value"
              animationBegin={isInView ? animationDelay * 1000 + 400 : 0}
              animationDuration={progressiveLoading ? 0 : 1000}
              animationEasing="ease-out"
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
              onClick={handleClick}
            >
              {chartData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`}
                  fill={entry.color}
                  stroke={hoveredIndex === index ? '#ffffff' : 'transparent'}
                  strokeWidth={hoveredIndex === index ? 2 : 0}
                  style={{
                    filter: hoveredIndex === index ? 'brightness(1.1) drop-shadow(0 0 8px rgba(0,0,0,0.3))' : 'none',
                    cursor: onSegmentClick ? 'pointer' : 'default',
                    transform: activeIndex === index ? 'scale(1.05)' : 'scale(1)',
                    transformOrigin: 'center',
                    transition: 'all 0.2s ease-in-out'
                  }}
                />
              ))}
            </Pie>
            
            {showTooltip && (
              <Tooltip 
                content={<CustomTooltip />}
                animationDuration={200}
              />
            )}
          </PieChart>
        </ResponsiveContainer>

        {/* Center Label */}
        <CenterLabel
          label={centerLabel}
          value={centerValue}
          isVisible={isInView}
          delay={animationDelay}
        />
      </motion.div>

      {/* Legend with progressive animation */}
      <motion.div
        variants={staggerConfigs.container}
        initial="initial"
        animate={isInView ? "animate" : "initial"}
        className="mt-4 space-y-2 max-h-32 overflow-y-auto"
      >
        {chartData.map((item, index) => (
          <motion.div
            key={item.name}
            variants={{
              initial: { opacity: 0, x: -20 },
              animate: { opacity: 1, x: 0 },
            }}
            transition={{ delay: (progressiveLoading ? index * 0.2 : 0) + animationDelay + 0.5 }}
            className={`flex items-center justify-between p-2 rounded-lg transition-all duration-200 ${
              onSegmentClick 
                ? 'hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer' 
                : ''
            }`}
            onClick={() => onSegmentClick?.(item)}
            whileHover={onSegmentClick ? { scale: 1.02, x: 4 } : undefined}
            whileTap={onSegmentClick ? { scale: 0.98 } : undefined}
          >
            <div className="flex items-center space-x-3 flex-1 min-w-0">
              <motion.div 
                className="w-3 h-3 rounded-full flex-shrink-0"
                style={{ backgroundColor: item.color }}
                whileHover={{ scale: 1.3 }}
                transition={springTransition}
              />
              <div className="min-w-0">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300 truncate block" title={item.name}>
                  {item.name}
                </span>
                {item.category && (
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {item.category}
                  </span>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-3 text-sm flex-shrink-0">
              <span className="font-medium text-gray-900 dark:text-white">
                {item.percentage.toFixed(1)}%
              </span>
              <span className="text-gray-500 dark:text-gray-400 text-xs">
                £{item.value.toLocaleString()}
              </span>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Summary */}
      <motion.div 
        className="border-t border-gray-200 dark:border-gray-700 pt-3 mt-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: isInView ? 1 : 0 }}
        transition={{ delay: animationDelay + 1, duration: 0.5 }}
      >
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">
            Total Allocation
          </span>
          <span className="font-medium text-gray-900 dark:text-white">
            £{chartData.reduce((sum, item) => sum + item.value, 0).toLocaleString()}
          </span>
        </div>
        
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
          <span>
            {chartData.length} sector{chartData.length !== 1 ? 's' : ''}
          </span>
          <span>
            {progressiveLoading ? 'Progressive load' : 'Live data'}
          </span>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default AnimatedDonutChart;