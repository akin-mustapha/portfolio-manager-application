import React, { useRef, useMemo } from 'react';
import { motion, useInView } from 'framer-motion';
import { Icon } from '../icons';
import { 
  springTransition, 
  smoothTransition,
  staggerConfigs
} from '../../utils/animations';

export interface AllocationData {
  name: string;
  currentPercentage: number;
  targetPercentage: number;
  currentValue: number;
  targetValue: number;
  drift: number; // Positive = overweight, Negative = underweight
  driftPercentage: number;
  category?: 'pie' | 'sector' | 'asset_type' | 'geography';
  color?: string;
}

interface AllocationDriftIndicatorsProps {
  data: AllocationData[];
  title?: string;
  loading?: boolean;
  showTargets?: boolean;
  driftThreshold?: number; // Threshold for highlighting significant drift
  animationDelay?: number;
  onItemClick?: (item: AllocationData) => void;
  className?: string;
}

// Drift severity levels
const getDriftSeverity = (driftPercentage: number, threshold: number = 5) => {
  const absDrift = Math.abs(driftPercentage);
  if (absDrift < threshold) return 'low';
  if (absDrift < threshold * 2) return 'medium';
  return 'high';
};

// Drift color mapping
const getDriftColor = (drift: number, severity: string) => {
  if (severity === 'low') return 'text-gray-600 dark:text-gray-400';
  
  if (drift > 0) {
    // Overweight
    return severity === 'high' 
      ? 'text-red-600 dark:text-red-400' 
      : 'text-orange-600 dark:text-orange-400';
  } else {
    // Underweight
    return severity === 'high' 
      ? 'text-blue-600 dark:text-blue-400' 
      : 'text-cyan-600 dark:text-cyan-400';
  }
};

// Drift background color
const getDriftBgColor = (drift: number, severity: string) => {
  if (severity === 'low') return 'bg-gray-100 dark:bg-gray-700';
  
  if (drift > 0) {
    // Overweight
    return severity === 'high' 
      ? 'bg-red-100 dark:bg-red-900/30' 
      : 'bg-orange-100 dark:bg-orange-900/30';
  } else {
    // Underweight
    return severity === 'high' 
      ? 'bg-blue-100 dark:bg-blue-900/30' 
      : 'bg-cyan-100 dark:bg-cyan-900/30';
  }
};

// Progress bar component with animation
const DriftProgressBar: React.FC<{
  current: number;
  target: number;
  drift: number;
  severity: string;
  isVisible: boolean;
  delay: number;
}> = ({ current, target, drift, severity, isVisible, delay }) => {
  const maxPercentage = Math.max(current, target, 50); // Ensure minimum scale
  const currentWidth = (current / maxPercentage) * 100;
  const targetWidth = (target / maxPercentage) * 100;

  return (
    <div className="relative h-6 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
      {/* Target line */}
      <motion.div
        className="absolute top-0 bottom-0 w-0.5 bg-gray-400 dark:bg-gray-500 z-20"
        style={{ left: `${targetWidth}%` }}
        initial={{ opacity: 0, scaleY: 0 }}
        animate={{ 
          opacity: isVisible ? 1 : 0, 
          scaleY: isVisible ? 1 : 0 
        }}
        transition={{ delay: delay + 0.3, ...springTransition }}
      />
      
      {/* Current allocation bar */}
      <motion.div
        className={`absolute top-0 bottom-0 rounded-full transition-colors duration-300 ${
          severity === 'low' 
            ? 'bg-green-500' 
            : drift > 0 
            ? 'bg-red-500' 
            : 'bg-blue-500'
        }`}
        initial={{ width: 0 }}
        animate={{ width: isVisible ? `${currentWidth}%` : 0 }}
        transition={{ delay, duration: 1, ease: 'easeOut' }}
      />
      
      {/* Drift indicator */}
      <motion.div
        className="absolute top-1/2 transform -translate-y-1/2 text-xs font-medium text-white px-2"
        style={{ left: `${Math.min(currentWidth - 10, 80)}%` }}
        initial={{ opacity: 0 }}
        animate={{ opacity: isVisible ? 1 : 0 }}
        transition={{ delay: delay + 0.5, duration: 0.5 }}
      >
        {current.toFixed(1)}%
      </motion.div>
      
      {/* Target indicator */}
      <motion.div
        className="absolute -top-6 text-xs text-gray-500 dark:text-gray-400"
        style={{ left: `${targetWidth}%`, transform: 'translateX(-50%)' }}
        initial={{ opacity: 0, y: 5 }}
        animate={{ 
          opacity: isVisible ? 1 : 0, 
          y: isVisible ? 0 : 5 
        }}
        transition={{ delay: delay + 0.4, duration: 0.4 }}
      >
        Target: {target.toFixed(1)}%
      </motion.div>
    </div>
  );
};

// Individual drift item component
const DriftItem: React.FC<{
  item: AllocationData;
  index: number;
  threshold: number;
  showTargets: boolean;
  isVisible: boolean;
  delay: number;
  onClick?: (item: AllocationData) => void;
}> = ({ item, index, threshold, showTargets, isVisible, delay, onClick }) => {
  const severity = getDriftSeverity(item.driftPercentage, threshold);
  const driftColor = getDriftColor(item.drift, severity);
  const driftBgColor = getDriftBgColor(item.drift, severity);
  
  const isOverweight = item.drift > 0;
  const isSignificant = severity !== 'low';

  return (
    <motion.div
      variants={{
        initial: { opacity: 0, y: 20 },
        animate: { opacity: 1, y: 0 },
      }}
      transition={{ delay: delay + index * 0.05, ...smoothTransition }}
      className={`p-4 rounded-lg border transition-all duration-300 ${
        isSignificant 
          ? `${driftBgColor} border-current` 
          : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700'
      } ${
        onClick ? 'hover:shadow-md cursor-pointer' : ''
      }`}
      onClick={() => onClick?.(item)}
      whileHover={onClick ? { scale: 1.02, y: -2 } : undefined}
      whileTap={onClick ? { scale: 0.98 } : undefined}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          {item.color && (
            <div 
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: item.color }}
            />
          )}
          <h4 className="font-medium text-gray-900 dark:text-white">
            {item.name}
          </h4>
          {item.category && (
            <span className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded-full">
              {item.category.replace('_', ' ')}
            </span>
          )}
        </div>
        
        {/* Drift indicator */}
        <motion.div 
          className={`flex items-center space-x-1 ${driftColor}`}
          whileHover={{ scale: 1.1 }}
          transition={springTransition}
        >
          <Icon 
            name={isOverweight ? 'TrendingUp' : 'TrendingDown'} 
            size="sm" 
          />
          <span className="font-medium text-sm">
            {isOverweight ? '+' : ''}{item.driftPercentage.toFixed(1)}%
          </span>
        </motion.div>
      </div>

      {/* Progress bar */}
      {showTargets && (
        <div className="mb-3">
          <DriftProgressBar
            current={item.currentPercentage}
            target={item.targetPercentage}
            drift={item.drift}
            severity={severity}
            isVisible={isVisible}
            delay={delay + index * 0.05 + 0.2}
          />
        </div>
      )}

      {/* Details */}
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-gray-600 dark:text-gray-400">Current</p>
          <p className="font-medium text-gray-900 dark:text-white">
            {item.currentPercentage.toFixed(1)}% (£{item.currentValue.toLocaleString()})
          </p>
        </div>
        
        {showTargets && (
          <div>
            <p className="text-gray-600 dark:text-gray-400">Target</p>
            <p className="font-medium text-gray-900 dark:text-white">
              {item.targetPercentage.toFixed(1)}% (£{item.targetValue.toLocaleString()})
            </p>
          </div>
        )}
      </div>

      {/* Severity indicator */}
      {isSignificant && (
        <motion.div 
          className="mt-3 pt-3 border-t border-current/20"
          initial={{ opacity: 0 }}
          animate={{ opacity: isVisible ? 1 : 0 }}
          transition={{ delay: delay + index * 0.05 + 0.5, duration: 0.4 }}
        >
          <div className={`flex items-center space-x-2 text-xs ${driftColor}`}>
            <Icon 
              name={severity === 'high' ? 'AlertTriangle' : 'Info'} 
              size="sm" 
            />
            <span>
              {severity === 'high' ? 'Significant' : 'Moderate'} {isOverweight ? 'overweight' : 'underweight'}
            </span>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

// Loading skeleton
const DriftSkeleton: React.FC<{ count: number }> = ({ count }) => (
  <div className="space-y-4">
    {[...Array(count)].map((_, index) => (
      <motion.div
        key={index}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.1, ...smoothTransition }}
        className="p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg"
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse" />
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-24" />
          </div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-16" />
        </div>
        
        <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse mb-3" />
        
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-12" />
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-20" />
          </div>
          <div className="space-y-1">
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-12" />
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-20" />
          </div>
        </div>
      </motion.div>
    ))}
  </div>
);

const AllocationDriftIndicators: React.FC<AllocationDriftIndicatorsProps> = ({
  data,
  title = "Allocation Drift Analysis",
  loading = false,
  showTargets = true,
  driftThreshold = 5,
  animationDelay = 0,
  onItemClick,
  className = ''
}) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });

  // Sort data by drift severity and magnitude
  const sortedData = useMemo(() => {
    return [...data].sort((a, b) => {
      const aSeverity = getDriftSeverity(a.driftPercentage, driftThreshold);
      const bSeverity = getDriftSeverity(b.driftPercentage, driftThreshold);
      
      // Sort by severity first, then by magnitude
      const severityOrder = { high: 3, medium: 2, low: 1 };
      const severityDiff = severityOrder[bSeverity as keyof typeof severityOrder] - severityOrder[aSeverity as keyof typeof severityOrder];
      
      if (severityDiff !== 0) return severityDiff;
      
      return Math.abs(b.driftPercentage) - Math.abs(a.driftPercentage);
    });
  }, [data, driftThreshold]);

  // Calculate summary statistics
  const summary = useMemo(() => {
    const significantDrifts = data.filter(item => 
      getDriftSeverity(item.driftPercentage, driftThreshold) !== 'low'
    );
    
    const overweightItems = data.filter(item => item.drift > 0);
    const underweightItems = data.filter(item => item.drift < 0);
    
    return {
      totalItems: data.length,
      significantDrifts: significantDrifts.length,
      overweightCount: overweightItems.length,
      underweightCount: underweightItems.length,
      maxDrift: Math.max(...data.map(item => Math.abs(item.driftPercentage))),
    };
  }, [data, driftThreshold]);

  if (loading) {
    return (
      <motion.div
        ref={ref}
        className={`bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border border-white/20 dark:border-gray-700/20 rounded-xl p-6 shadow-soft ${className}`}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: animationDelay, ...smoothTransition }}
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          {title}
        </h3>
        <DriftSkeleton count={5} />
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
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          {title}
        </h3>
        
        <div className="text-center py-8">
          <div className="text-gray-400 mb-2">
            <Icon name="Target" size="2xl" />
          </div>
          <p className="text-gray-500 font-medium">No allocation data available</p>
          <p className="text-gray-400 text-sm mt-1">
            Drift analysis will appear when targets are set
          </p>
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
      whileHover={{ scale: 1.005 }}
    >
      {/* Header */}
      <motion.div
        className="flex items-center justify-between mb-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: isInView ? 1 : 0 }}
        transition={{ delay: animationDelay + 0.2, duration: 0.5 }}
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          {title}
        </h3>
        
        {/* Summary stats */}
        <div className="flex items-center space-x-4 text-sm">
          <div className="text-center">
            <div className="font-medium text-gray-900 dark:text-white">
              {summary.significantDrifts}
            </div>
            <div className="text-gray-500 dark:text-gray-400">
              Significant
            </div>
          </div>
          
          <div className="text-center">
            <div className="font-medium text-red-600 dark:text-red-400">
              {summary.overweightCount}
            </div>
            <div className="text-gray-500 dark:text-gray-400">
              Over
            </div>
          </div>
          
          <div className="text-center">
            <div className="font-medium text-blue-600 dark:text-blue-400">
              {summary.underweightCount}
            </div>
            <div className="text-gray-500 dark:text-gray-400">
              Under
            </div>
          </div>
        </div>
      </motion.div>

      {/* Drift items */}
      <motion.div
        variants={staggerConfigs.container}
        initial="initial"
        animate={isInView ? "animate" : "initial"}
        className="space-y-4"
      >
        {sortedData.map((item, index) => (
          <DriftItem
            key={item.name}
            item={item}
            index={index}
            threshold={driftThreshold}
            showTargets={showTargets}
            isVisible={isInView}
            delay={animationDelay + 0.4}
            onClick={onItemClick}
          />
        ))}
      </motion.div>

      {/* Summary */}
      <motion.div 
        className="border-t border-gray-200 dark:border-gray-700 pt-4 mt-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: isInView ? 1 : 0 }}
        transition={{ delay: animationDelay + 1, duration: 0.5 }}
      >
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">
            Maximum Drift
          </span>
          <span className="font-medium text-gray-900 dark:text-white">
            {summary.maxDrift.toFixed(1)}%
          </span>
        </div>
        
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
          <span>
            Threshold: ±{driftThreshold}%
          </span>
          <span>
            {summary.totalItems} allocations tracked
          </span>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default AllocationDriftIndicators;