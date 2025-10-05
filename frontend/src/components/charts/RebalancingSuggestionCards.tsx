import React, { useState, useRef, useMemo } from 'react';
import { motion, AnimatePresence, useInView } from 'framer-motion';
import { Icon } from '../icons';
import { 
  springTransition, 
  smoothTransition,
  staggerConfigs,
  hoverVariants
} from '../../utils/animations';

export interface RebalancingSuggestion {
  id: string;
  type: 'buy' | 'sell' | 'rebalance';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  currentAllocation: number;
  targetAllocation: number;
  suggestedAmount: number;
  impact: {
    driftReduction: number;
    riskImprovement?: number;
    costEstimate?: number;
  };
  assets: {
    name: string;
    symbol: string;
    action: 'buy' | 'sell';
    amount: number;
    percentage: number;
  }[];
  reasoning: string[];
  estimatedTime: string;
  difficulty: 'easy' | 'moderate' | 'complex';
}

interface RebalancingSuggestionCardsProps {
  suggestions: RebalancingSuggestion[];
  title?: string;
  loading?: boolean;
  maxSuggestions?: number;
  showPriorityFilter?: boolean;
  animationDelay?: number;
  onSuggestionAccept?: (suggestion: RebalancingSuggestion) => void;
  onSuggestionDismiss?: (suggestion: RebalancingSuggestion) => void;
  className?: string;
}

// Priority configuration
const PRIORITY_CONFIG = {
  high: {
    color: 'text-red-600 dark:text-red-400',
    bgColor: 'bg-red-50 dark:bg-red-900/20',
    borderColor: 'border-red-200 dark:border-red-800',
    icon: 'AlertTriangle' as const,
    label: 'High Priority'
  },
  medium: {
    color: 'text-orange-600 dark:text-orange-400',
    bgColor: 'bg-orange-50 dark:bg-orange-900/20',
    borderColor: 'border-orange-200 dark:border-orange-800',
    icon: 'Info' as const,
    label: 'Medium Priority'
  },
  low: {
    color: 'text-blue-600 dark:text-blue-400',
    bgColor: 'bg-blue-50 dark:bg-blue-900/20',
    borderColor: 'border-blue-200 dark:border-blue-800',
    icon: 'CheckCircle' as const,
    label: 'Low Priority'
  }
};

// Type configuration
const TYPE_CONFIG = {
  buy: {
    color: 'text-green-600 dark:text-green-400',
    bgColor: 'bg-green-100 dark:bg-green-900/30',
    icon: 'TrendingUp' as const,
    label: 'Buy'
  },
  sell: {
    color: 'text-red-600 dark:text-red-400',
    bgColor: 'bg-red-100 dark:bg-red-900/30',
    icon: 'TrendingDown' as const,
    label: 'Sell'
  },
  rebalance: {
    color: 'text-purple-600 dark:text-purple-400',
    bgColor: 'bg-purple-100 dark:bg-purple-900/30',
    icon: 'BarChart' as const,
    label: 'Rebalance'
  }
};

// Difficulty configuration
const DIFFICULTY_CONFIG = {
  easy: {
    color: 'text-green-600 dark:text-green-400',
    label: 'Easy',
    icon: 'CheckCircle' as const
  },
  moderate: {
    color: 'text-orange-600 dark:text-orange-400',
    label: 'Moderate',
    icon: 'Clock' as const
  },
  complex: {
    color: 'text-red-600 dark:text-red-400',
    label: 'Complex',
    icon: 'AlertTriangle' as const
  }
};

// Asset action component
const AssetAction: React.FC<{
  asset: RebalancingSuggestion['assets'][0];
  index: number;
  isVisible: boolean;
  delay: number;
}> = ({ asset, index, isVisible, delay }) => {
  const actionConfig = TYPE_CONFIG[asset.action];

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ 
        opacity: isVisible ? 1 : 0, 
        x: isVisible ? 0 : -10 
      }}
      transition={{ delay: delay + index * 0.05, ...smoothTransition }}
      className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded-lg"
    >
      <div className="flex items-center space-x-2">
        <div className={`p-1 rounded ${actionConfig.bgColor}`}>
          <Icon 
            name={actionConfig.icon} 
            size="sm" 
            className={actionConfig.color}
          />
        </div>
        <div>
          <p className="text-sm font-medium text-gray-900 dark:text-white">
            {asset.symbol}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
            {asset.name}
          </p>
        </div>
      </div>
      
      <div className="text-right">
        <p className={`text-sm font-medium ${actionConfig.color}`}>
          {asset.action === 'buy' ? '+' : '-'}£{asset.amount.toLocaleString()}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          {asset.percentage.toFixed(1)}%
        </p>
      </div>
    </motion.div>
  );
};

// Impact metrics component
const ImpactMetrics: React.FC<{
  impact: RebalancingSuggestion['impact'];
  isVisible: boolean;
  delay: number;
}> = ({ impact, isVisible, delay }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ 
      opacity: isVisible ? 1 : 0, 
      y: isVisible ? 0 : 10 
    }}
    transition={{ delay, ...smoothTransition }}
    className="grid grid-cols-2 gap-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
  >
    <div className="text-center">
      <p className="text-lg font-bold text-green-600 dark:text-green-400">
        -{impact.driftReduction.toFixed(1)}%
      </p>
      <p className="text-xs text-gray-500 dark:text-gray-400">
        Drift Reduction
      </p>
    </div>
    
    {impact.riskImprovement && (
      <div className="text-center">
        <p className="text-lg font-bold text-blue-600 dark:text-blue-400">
          +{impact.riskImprovement.toFixed(1)}%
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Risk Score
        </p>
      </div>
    )}
    
    {impact.costEstimate && (
      <div className="text-center col-span-2">
        <p className="text-sm font-medium text-gray-900 dark:text-white">
          Est. Cost: £{impact.costEstimate.toFixed(2)}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Trading fees & spread
        </p>
      </div>
    )}
  </motion.div>
);

// Individual suggestion card
const SuggestionCard: React.FC<{
  suggestion: RebalancingSuggestion;
  index: number;
  isVisible: boolean;
  delay: number;
  onAccept?: (suggestion: RebalancingSuggestion) => void;
  onDismiss?: (suggestion: RebalancingSuggestion) => void;
}> = ({ suggestion, index, isVisible, delay, onAccept, onDismiss }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  
  const priorityConfig = PRIORITY_CONFIG[suggestion.priority];
  const typeConfig = TYPE_CONFIG[suggestion.type];
  const difficultyConfig = DIFFICULTY_CONFIG[suggestion.difficulty];

  const handleAccept = async () => {
    setIsProcessing(true);
    await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
    onAccept?.(suggestion);
    setIsProcessing(false);
  };

  const handleDismiss = () => {
    onDismiss?.(suggestion);
  };

  return (
    <motion.div
      variants={{
        initial: { opacity: 0, y: 20, scale: 0.95 },
        animate: { opacity: 1, y: 0, scale: 1 },
      }}
      transition={{ delay: delay + index * 0.1, ...springTransition }}
      className={`relative overflow-hidden rounded-xl border-2 transition-all duration-300 ${priorityConfig.borderColor} ${priorityConfig.bgColor} hover:shadow-lg`}
      whileHover={{ scale: 1.02, y: -2 }}
    >
      {/* Priority indicator */}
      <div className={`absolute top-0 left-0 right-0 h-1 ${
        suggestion.priority === 'high' ? 'bg-red-500' :
        suggestion.priority === 'medium' ? 'bg-orange-500' : 'bg-blue-500'
      }`} />

      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <div className={`p-1.5 rounded-lg ${typeConfig.bgColor}`}>
                <Icon 
                  name={typeConfig.icon} 
                  size="sm" 
                  className={typeConfig.color}
                />
              </div>
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${priorityConfig.bgColor} ${priorityConfig.color}`}>
                {priorityConfig.label}
              </span>
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${difficultyConfig.color} bg-gray-100 dark:bg-gray-700`}>
                {difficultyConfig.label}
              </span>
            </div>
            
            <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
              {suggestion.title}
            </h4>
            
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {suggestion.description}
            </p>
          </div>

          <motion.button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <motion.div
              animate={{ rotate: isExpanded ? 180 : 0 }}
              transition={springTransition}
            >
              <Icon name="ChevronDown" size="sm" />
            </motion.div>
          </motion.button>
        </div>

        {/* Key metrics */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="text-center">
            <p className="text-sm text-gray-500 dark:text-gray-400">Current</p>
            <p className="font-medium text-gray-900 dark:text-white">
              {suggestion.currentAllocation.toFixed(1)}%
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-500 dark:text-gray-400">Target</p>
            <p className="font-medium text-gray-900 dark:text-white">
              {suggestion.targetAllocation.toFixed(1)}%
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-500 dark:text-gray-400">Amount</p>
            <p className="font-medium text-gray-900 dark:text-white">
              £{suggestion.suggestedAmount.toLocaleString()}
            </p>
          </div>
        </div>

        {/* Expanded content */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
              className="space-y-4"
            >
              {/* Impact metrics */}
              <div>
                <h5 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Expected Impact
                </h5>
                <ImpactMetrics
                  impact={suggestion.impact}
                  isVisible={isExpanded}
                  delay={0.1}
                />
              </div>

              {/* Asset actions */}
              <div>
                <h5 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Suggested Actions
                </h5>
                <div className="space-y-2">
                  {suggestion.assets.map((asset, assetIndex) => (
                    <AssetAction
                      key={`${asset.symbol}-${assetIndex}`}
                      asset={asset}
                      index={assetIndex}
                      isVisible={isExpanded}
                      delay={0.2}
                    />
                  ))}
                </div>
              </div>

              {/* Reasoning */}
              <div>
                <h5 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                  Reasoning
                </h5>
                <ul className="space-y-1">
                  {suggestion.reasoning.map((reason, reasonIndex) => (
                    <motion.li
                      key={reasonIndex}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.3 + reasonIndex * 0.05, ...smoothTransition }}
                      className="flex items-start space-x-2 text-sm text-gray-600 dark:text-gray-400"
                    >
                      <Icon name="CheckCircle" size="sm" className="text-green-500 mt-0.5 flex-shrink-0" />
                      <span>{reason}</span>
                    </motion.li>
                  ))}
                </ul>
              </div>

              {/* Estimated time */}
              <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                <Icon name="Clock" size="sm" />
                <span>Estimated time: {suggestion.estimatedTime}</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Action buttons */}
        <div className="flex items-center space-x-3 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <motion.button
            onClick={handleAccept}
            disabled={isProcessing}
            className={`flex-1 px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200 ${
              isProcessing
                ? 'bg-gray-300 dark:bg-gray-600 text-gray-500 cursor-not-allowed'
                : 'bg-primary-500 hover:bg-primary-600 text-white shadow-sm hover:shadow-md'
            }`}
            whileHover={!isProcessing ? { scale: 1.02 } : undefined}
            whileTap={!isProcessing ? { scale: 0.98 } : undefined}
          >
            {isProcessing ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                <span>Processing...</span>
              </div>
            ) : (
              <div className="flex items-center justify-center space-x-2">
                <Icon name="CheckCircle" size="sm" />
                <span>Accept Suggestion</span>
              </div>
            )}
          </motion.button>

          <motion.button
            onClick={handleDismiss}
            className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Icon name="X" size="sm" />
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
};

// Loading skeleton
const SuggestionSkeleton: React.FC<{ count: number }> = ({ count }) => (
  <div className="space-y-6">
    {[...Array(count)].map((_, index) => (
      <motion.div
        key={index}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: index * 0.1, ...smoothTransition }}
        className="p-6 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl"
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse" />
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-20" />
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-16" />
            </div>
            <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-48 mb-2" />
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-64" />
          </div>
          <div className="w-6 h-6 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        </div>
        
        <div className="grid grid-cols-3 gap-4 mb-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="text-center">
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-12 mx-auto mb-1" />
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-16 mx-auto" />
            </div>
          ))}
        </div>
        
        <div className="flex space-x-3">
          <div className="flex-1 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse" />
          <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse" />
        </div>
      </motion.div>
    ))}
  </div>
);

const RebalancingSuggestionCards: React.FC<RebalancingSuggestionCardsProps> = ({
  suggestions,
  title = "Rebalancing Suggestions",
  loading = false,
  maxSuggestions = 5,
  showPriorityFilter = true,
  animationDelay = 0,
  onSuggestionAccept,
  onSuggestionDismiss,
  className = ''
}) => {
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });

  // Filter and sort suggestions
  const filteredSuggestions = useMemo(() => {
    let filtered = suggestions;
    
    if (priorityFilter !== 'all') {
      filtered = filtered.filter(s => s.priority === priorityFilter);
    }
    
    // Sort by priority (high -> medium -> low) then by impact
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    filtered.sort((a, b) => {
      const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
      if (priorityDiff !== 0) return priorityDiff;
      return b.impact.driftReduction - a.impact.driftReduction;
    });
    
    return filtered.slice(0, maxSuggestions);
  }, [suggestions, priorityFilter, maxSuggestions]);

  // Summary statistics
  const summary = useMemo(() => {
    const highPriority = suggestions.filter(s => s.priority === 'high').length;
    const totalImpact = suggestions.reduce((sum, s) => sum + s.impact.driftReduction, 0);
    const totalAmount = suggestions.reduce((sum, s) => sum + s.suggestedAmount, 0);
    
    return { highPriority, totalImpact, totalAmount };
  }, [suggestions]);

  if (loading) {
    return (
      <motion.div
        ref={ref}
        className={`bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border border-white/20 dark:border-gray-700/20 rounded-xl p-6 shadow-soft ${className}`}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: animationDelay, ...smoothTransition }}
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
          {title}
        </h3>
        <SuggestionSkeleton count={3} />
      </motion.div>
    );
  }

  if (!suggestions || suggestions.length === 0) {
    return (
      <motion.div
        ref={ref}
        className={`bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border border-white/20 dark:border-gray-700/20 rounded-xl p-6 shadow-soft ${className}`}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: animationDelay, ...smoothTransition }}
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">
          {title}
        </h3>
        
        <div className="text-center py-8">
          <div className="text-gray-400 mb-2">
            <Icon name="CheckCircle" size="2xl" />
          </div>
          <p className="text-gray-500 font-medium">Portfolio is well balanced</p>
          <p className="text-gray-400 text-sm mt-1">
            No rebalancing suggestions at this time
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
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {title}
          </h3>
          <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500 dark:text-gray-400">
            <span>{summary.highPriority} high priority</span>
            <span>•</span>
            <span>{summary.totalImpact.toFixed(1)}% total drift reduction</span>
            <span>•</span>
            <span>£{summary.totalAmount.toLocaleString()} suggested</span>
          </div>
        </div>

        {/* Priority filter */}
        {showPriorityFilter && (
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="all">All Priorities</option>
            <option value="high">High Priority</option>
            <option value="medium">Medium Priority</option>
            <option value="low">Low Priority</option>
          </select>
        )}
      </motion.div>

      {/* Suggestions */}
      <motion.div
        variants={staggerConfigs.container}
        initial="initial"
        animate={isInView ? "animate" : "initial"}
        className="space-y-6"
      >
        {filteredSuggestions.map((suggestion, index) => (
          <SuggestionCard
            key={suggestion.id}
            suggestion={suggestion}
            index={index}
            isVisible={isInView}
            delay={animationDelay + 0.4}
            onAccept={onSuggestionAccept}
            onDismiss={onSuggestionDismiss}
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
        <div className="text-center text-sm text-gray-500 dark:text-gray-400">
          Showing {filteredSuggestions.length} of {suggestions.length} suggestions
          {filteredSuggestions.length < suggestions.length && (
            <span> • <button className="text-primary-500 hover:text-primary-600 transition-colors">View all</button></span>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default RebalancingSuggestionCards;