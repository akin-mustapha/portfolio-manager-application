import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, useInView } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { Icon } from '../icons';
import { 
  springTransition, 
  smoothTransition,
  chartAnimations,
  staggerConfigs
} from '../../utils/animations';

export interface PieChartData {
  name: string;
  value: number;
  percentage: number;
  color?: string;
  sector?: string;
  change?: number;
}

interface InteractivePieChartProps {
  data: PieChartData[];
  title?: string;
  loading?: boolean;
  height?: number;
  showLegend?: boolean;
  showTooltip?: boolean;
  animationDelay?: number;
  onSegmentClick?: (data: PieChartData) => void;
  className?: string;
}

// Default color palette for pie segments
const DEFAULT_COLORS = [
  '#3B82F6', // blue-500
  '#10B981', // emerald-500
  '#F59E0B', // amber-500
  '#EF4444', // red-500
  '#8B5CF6', // violet-500
  '#06B6D4', // cyan-500
  '#84CC16', // lime-500
  '#F97316', // orange-500
  '#EC4899', // pink-500
  '#6B7280', // gray-500
  '#14B8A6', // teal-500
  '#F97316', // orange-500
];

// Custom tooltip component with animations
const CustomTooltip: React.FC<any> = ({ active, payload, label }) => {
  if (!active || !payload || !payload.length) return null;

  const data = payload[0].payload;
  
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, y: 10 }}
      transition={smoothTransition}
      className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-md border border-gray-200 dark:border-gray-700 rounded-lg p-3 shadow-lg"
    >
      <div className="flex items-center space-x-2 mb-2">
        <div 
          className="w-3 h-3 rounded-full"
          style={{ backgroundColor: data.color }}
        />
        <span className="font-medium text-gray-900 dark:text-white">
          {data.name}
        </span>
      </div>
      
      <div className="space-y-1 text-sm">
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
        
        {data.sector && (
          <div className="flex justify-between items-center">
            <span className="text-gray-600 dark:text-gray-400">Sector:</span>
            <span className="font-medium text-gray-900 dark:text-white">
              {data.sector}
            </span>
          </div>
        )}
        
        {data.change !== undefined && (
          <div className="flex justify-between items-center">
            <span className="text-gray-600 dark:text-gray-400">Change:</span>
            <span className={`font-medium flex items-center ${
              data.change >= 0 
                ? 'text-green-600 dark:text-green-400' 
                : 'text-red-600 dark:text-red-400'
            }`}>
              <Icon 
                name={data.change >= 0 ? 'TrendingUp' : 'TrendingDown'} 
                size="sm" 
                className="mr-1"
              />
              {Math.abs(data.change).toFixed(2)}%
            </span>
          </div>
        )}
      </div>
    </motion.div>
  );
};

// Custom legend component with animations
const CustomLegend: React.FC<{ data: PieChartData[]; onItemClick?: (data: PieChartData) => void }> = ({ 
  data, 
  onItemClick 
}) => {
  return (
    <motion.div
      variants={staggerConfigs.container}
      initial="initial"
      animate="animate"
      className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-4"
    >
      {data.map((item, index) => (
        <motion.div
          key={item.name}
          variants={{
            initial: { opacity: 0, x: -20 },
            animate: { opacity: 1, x: 0 },
          }}
          transition={{ delay: index * 0.05 }}
          className={`flex items-center justify-between p-2 rounded-lg transition-all duration-200 ${
            onItemClick 
              ? 'hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer' 
              : ''
          }`}
          onClick={() => onItemClick?.(item)}
          whileHover={onItemClick ? { scale: 1.02 } : undefined}
          whileTap={onItemClick ? { scale: 0.98 } : undefined}
        >
          <div className="flex items-center space-x-2 flex-1 min-w-0">
            <motion.div 
              className="w-3 h-3 rounded-full flex-shrink-0"
              style={{ backgroundColor: item.color }}
              whileHover={{ scale: 1.2 }}
              transition={springTransition}
            />
            <span className="text-sm text-gray-700 dark:text-gray-300 truncate" title={item.name}>
              {item.name}
            </span>
          </div>
          
          <div className="flex items-center space-x-3 text-sm flex-shrink-0">
            <span className="font-medium text-gray-900 dark:text-white">
              {item.percentage.toFixed(1)}%
            </span>
            <span className="text-gray-500 dark:text-gray-400">
              £{item.value.toLocaleString()}
            </span>
          </div>
        </motion.div>
      ))}
    </motion.div>
  );
};

// Loading skeleton component
const PieChartSkeleton: React.FC<{ height: number }> = ({ height }) => (
  <div className="flex items-center justify-center" style={{ height }}>
    <div className="space-y-4 w-full max-w-md">
      {/* Pie chart skeleton */}
      <div className="flex justify-center">
        <div className="relative">
          <div className="w-48 h-48 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse" />
          <div className="absolute inset-6 bg-white dark:bg-gray-800 rounded-full" />
        </div>
      </div>
      
      {/* Legend skeleton */}
      <div className="space-y-2">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="flex items-center justify-between p-2">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse" />
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-20" />
            </div>
            <div className="flex space-x-2">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-12" />
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-16" />
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const InteractivePieChart: React.FC<InteractivePieChartProps> = ({
  data,
  title,
  loading = false,
  height = 400,
  showLegend = true,
  showTooltip = true,
  animationDelay = 0,
  onSegmentClick,
  className = ''
}) => {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });

  // Prepare data with colors
  const chartData = data.map((item, index) => ({
    ...item,
    color: item.color || DEFAULT_COLORS[index % DEFAULT_COLORS.length]
  }));

  // Handle segment interactions
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
        <PieChartSkeleton height={height} />
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
            <p className="text-gray-500 font-medium">No data available</p>
            <p className="text-gray-400 text-sm mt-1">
              Data will appear when available
            </p>
          </div>
        </div>
      </motion.div>
    );
  }

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
              outerRadius={Math.min(height * 0.35, 120)}
              innerRadius={Math.min(height * 0.15, 50)}
              paddingAngle={2}
              dataKey="value"
              animationBegin={isInView ? animationDelay * 1000 + 400 : 0}
              animationDuration={1200}
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
                  strokeWidth={hoveredIndex === index ? 3 : 0}
                  style={{
                    filter: hoveredIndex === index ? 'brightness(1.1)' : 'none',
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
      </motion.div>

      {/* Custom Legend */}
      {showLegend && (
        <AnimatePresence>
          <CustomLegend 
            data={chartData} 
            onItemClick={onSegmentClick}
          />
        </AnimatePresence>
      )}

      {/* Summary */}
      <motion.div 
        className="border-t border-gray-200 dark:border-gray-700 pt-4 mt-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: isInView ? 1 : 0 }}
        transition={{ delay: animationDelay + 0.8, duration: 0.5 }}
      >
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">
            Total Value
          </span>
          <span className="font-medium text-gray-900 dark:text-white">
            £{chartData.reduce((sum, item) => sum + item.value, 0).toLocaleString()}
          </span>
        </div>
        
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
          <span>
            {chartData.length} segment{chartData.length !== 1 ? 's' : ''}
          </span>
          <span>
            Live allocation
          </span>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default InteractivePieChart;