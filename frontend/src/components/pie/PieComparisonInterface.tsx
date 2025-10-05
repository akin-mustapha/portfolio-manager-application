import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Pie } from '../../types/api';
import AnimatedMetricCard from '../AnimatedMetricCard';
import { Icon } from '../icons';
import { Button } from '../ui/Button';
import { containerVariants, listItemVariants, springTransition } from '../../utils/animations';

interface PieComparisonInterfaceProps {
  selectedPies: Pie[];
  availablePies: Pie[];
  loading?: boolean;
  onPieAdd: (pie: Pie) => void;
  onPieRemove: (pieId: string) => void;
}

type ComparisonMetric = 'return' | 'value' | 'volatility' | 'sharpe' | 'drawdown';

const PieComparisonInterface: React.FC<PieComparisonInterfaceProps> = ({
  selectedPies,
  availablePies,
  loading = false,
  onPieAdd,
  onPieRemove
}) => {
  const [comparisonMetric, setComparisonMetric] = useState<ComparisonMetric>('return');
  const [showAddPieModal, setShowAddPieModal] = useState(false);

  const availableToAdd = availablePies.filter(
    pie => !selectedPies.find(selected => selected.id === pie.id)
  );

  const comparisonMetrics = {
    return: { label: 'Return %', icon: 'TrendingUp', format: (val: number) => `${val.toFixed(2)}%` },
    value: { label: 'Total Value', icon: 'DollarSign', format: (val: number) => `£${val.toLocaleString()}` },
    volatility: { label: 'Volatility', icon: 'Activity', format: (val: number) => `${val.toFixed(1)}%` },
    sharpe: { label: 'Sharpe Ratio', icon: 'BarChart', format: (val: number) => val.toFixed(2) },
    drawdown: { label: 'Max Drawdown', icon: 'TrendingDown', format: (val: number) => `${val.toFixed(1)}%` }
  };

  const getMetricValue = (pie: Pie, metric: ComparisonMetric): number => {
    switch (metric) {
      case 'return':
        return pie.returnPercentage;
      case 'value':
        return pie.totalValue;
      case 'volatility':
        return Math.random() * 20 + 5; // Mock data
      case 'sharpe':
        return Math.random() * 2 + 0.5; // Mock data
      case 'drawdown':
        return -(Math.random() * 15 + 2); // Mock data
      default:
        return 0;
    }
  };

  const getBestPerformer = (metric: ComparisonMetric) => {
    if (selectedPies.length === 0) return null;
    
    return selectedPies.reduce((best, current) => {
      const currentValue = getMetricValue(current, metric);
      const bestValue = getMetricValue(best, metric);
      
      // For drawdown, lower (more negative) is worse, so we want higher (less negative)
      if (metric === 'drawdown') {
        return currentValue > bestValue ? current : best;
      }
      
      return currentValue > bestValue ? current : best;
    });
  };

  const getWorstPerformer = (metric: ComparisonMetric) => {
    if (selectedPies.length === 0) return null;
    
    return selectedPies.reduce((worst, current) => {
      const currentValue = getMetricValue(current, metric);
      const worstValue = getMetricValue(worst, metric);
      
      // For drawdown, lower (more negative) is worse
      if (metric === 'drawdown') {
        return currentValue < worstValue ? current : worst;
      }
      
      return currentValue < worstValue ? current : worst;
    });
  };

  const bestPerformer = getBestPerformer(comparisonMetric);
  const worstPerformer = getWorstPerformer(comparisonMetric);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(3)].map((_, index) => (
            <div key={index} className="animate-pulse">
              <div className="bg-gray-200 rounded-lg h-48"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4"
      >
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Pie Comparison ({selectedPies.length}/4)
          </h2>
          <p className="text-gray-600">
            Compare performance metrics across your selected pies
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {/* Metric Selector */}
          <select
            value={comparisonMetric}
            onChange={(e) => setComparisonMetric(e.target.value as ComparisonMetric)}
            className="px-4 py-2 border border-gray-300 rounded-lg bg-white/80 backdrop-blur-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {Object.entries(comparisonMetrics).map(([key, config]) => (
              <option key={key} value={key}>
                {config.label}
              </option>
            ))}
          </select>

          {/* Add Pie Button */}
          <Button
            onClick={() => setShowAddPieModal(true)}
            disabled={selectedPies.length >= 4 || availableToAdd.length === 0}
            className="flex items-center space-x-2"
          >
            <Icon name="Plus" size="sm" />
            <span>Add Pie</span>
          </Button>
        </div>
      </motion.div>

      {/* Comparison Cards */}
      <motion.div
        variants={containerVariants}
        initial="initial"
        animate="animate"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
      >
        <AnimatePresence>
          {selectedPies.map((pie, index) => {
            const metricValue = getMetricValue(pie, comparisonMetric);
            const isBest = bestPerformer?.id === pie.id;
            const isWorst = worstPerformer?.id === pie.id && selectedPies.length > 1;
            
            return (
              <motion.div
                key={pie.id}
                variants={listItemVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                layout
                className={`
                  relative bg-white/80 backdrop-blur-sm rounded-xl p-6 border-2 transition-all duration-300
                  ${isBest ? 'border-green-400 bg-green-50/50' : 
                    isWorst ? 'border-red-400 bg-red-50/50' : 
                    'border-gray-200 hover:border-blue-300'}
                `}
              >
                {/* Performance Badge */}
                {isBest && (
                  <motion.div
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="absolute -top-2 -right-2 bg-green-500 text-white text-xs font-bold px-2 py-1 rounded-full"
                  >
                    BEST
                  </motion.div>
                )}
                {isWorst && (
                  <motion.div
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full"
                  >
                    WORST
                  </motion.div>
                )}

                {/* Remove Button */}
                <motion.button
                  onClick={() => onPieRemove(pie.id)}
                  className="absolute top-2 right-2 text-gray-400 hover:text-red-500 transition-colors"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <Icon name="X" size="sm" />
                </motion.button>

                {/* Pie Info */}
                <div className="mb-4">
                  <h3 className="font-semibold text-gray-900 mb-1 pr-6">
                    {pie.name}
                  </h3>
                  <p className="text-sm text-gray-500">
                    £{pie.totalValue.toLocaleString()}
                  </p>
                </div>

                {/* Main Metric */}
                <div className="mb-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <Icon name={comparisonMetrics[comparisonMetric].icon as any} size="sm" />
                    <span className="text-sm font-medium text-gray-600">
                      {comparisonMetrics[comparisonMetric].label}
                    </span>
                  </div>
                  <div className={`text-2xl font-bold ${
                    comparisonMetric === 'return' 
                      ? metricValue >= 0 ? 'text-green-600' : 'text-red-600'
                      : 'text-gray-900'
                  }`}>
                    {comparisonMetrics[comparisonMetric].format(metricValue)}
                  </div>
                </div>

                {/* Additional Metrics */}
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Return:</span>
                    <span className={pie.returnPercentage >= 0 ? 'text-green-600' : 'text-red-600'}>
                      {pie.returnPercentage.toFixed(2)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Invested:</span>
                    <span>£{pie.investedAmount.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Positions:</span>
                    <span>{pie.positions?.length || 0}</span>
                  </div>
                </div>

                {/* Progress Bar for Relative Performance */}
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <motion.div
                      className={`h-2 rounded-full ${
                        isBest ? 'bg-green-500' : 
                        isWorst ? 'bg-red-500' : 
                        'bg-blue-500'
                      }`}
                      initial={{ width: 0 }}
                      animate={{ 
                        width: selectedPies.length > 1 
                          ? `${((metricValue - Math.min(...selectedPies.map(p => getMetricValue(p, comparisonMetric)))) / 
                              (Math.max(...selectedPies.map(p => getMetricValue(p, comparisonMetric))) - 
                               Math.min(...selectedPies.map(p => getMetricValue(p, comparisonMetric))))) * 100}%`
                          : '100%'
                      }}
                      transition={{ duration: 0.8, delay: index * 0.1 }}
                    />
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {/* Add Pie Placeholder */}
        {selectedPies.length < 4 && (
          <motion.button
            onClick={() => setShowAddPieModal(true)}
            className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center hover:border-blue-400 hover:bg-blue-50/50 transition-all duration-300"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            disabled={availableToAdd.length === 0}
          >
            <div className="text-gray-400 mb-2">
              <Icon name="Plus" size="2xl" />
            </div>
            <p className="text-gray-600 font-medium">Add Pie to Compare</p>
            <p className="text-sm text-gray-500 mt-1">
              {availableToAdd.length} available
            </p>
          </motion.button>
        )}
      </motion.div>

      {/* Summary Stats */}
      {selectedPies.length > 1 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white/80 backdrop-blur-sm rounded-xl p-6 border border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Comparison Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600 mb-1">
                {bestPerformer ? comparisonMetrics[comparisonMetric].format(getMetricValue(bestPerformer, comparisonMetric)) : '-'}
              </div>
              <div className="text-sm text-gray-600">Best {comparisonMetrics[comparisonMetric].label}</div>
              <div className="text-xs text-gray-500 mt-1">{bestPerformer?.name}</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900 mb-1">
                {selectedPies.length > 0 
                  ? comparisonMetrics[comparisonMetric].format(
                      selectedPies.reduce((sum, pie) => sum + getMetricValue(pie, comparisonMetric), 0) / selectedPies.length
                    )
                  : '-'
                }
              </div>
              <div className="text-sm text-gray-600">Average {comparisonMetrics[comparisonMetric].label}</div>
              <div className="text-xs text-gray-500 mt-1">Across {selectedPies.length} pies</div>
            </div>
            
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600 mb-1">
                {worstPerformer ? comparisonMetrics[comparisonMetric].format(getMetricValue(worstPerformer, comparisonMetric)) : '-'}
              </div>
              <div className="text-sm text-gray-600">Worst {comparisonMetrics[comparisonMetric].label}</div>
              <div className="text-xs text-gray-500 mt-1">{worstPerformer?.name}</div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Add Pie Modal */}
      <AnimatePresence>
        {showAddPieModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
            onClick={() => setShowAddPieModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={springTransition}
              className="bg-white rounded-xl p-6 max-w-md w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Add Pie to Comparison</h3>
                <button
                  onClick={() => setShowAddPieModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <Icon name="X" size="sm" />
                </button>
              </div>
              
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {availableToAdd.map((pie) => (
                  <motion.button
                    key={pie.id}
                    onClick={() => {
                      onPieAdd(pie);
                      setShowAddPieModal(false);
                    }}
                    className="w-full text-left p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50/50 transition-all duration-200"
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                  >
                    <div className="font-medium text-gray-900">{pie.name}</div>
                    <div className="text-sm text-gray-500">
                      £{pie.totalValue.toLocaleString()} • {pie.returnPercentage.toFixed(2)}% return
                    </div>
                  </motion.button>
                ))}
              </div>
              
              {availableToAdd.length === 0 && (
                <p className="text-center text-gray-500 py-4">
                  No more pies available to add
                </p>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Empty State */}
      {selectedPies.length === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-12"
        >
          <div className="text-gray-400 mb-4">
            <Icon name="BarChart3" size="2xl" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            No Pies Selected for Comparison
          </h3>
          <p className="text-gray-600 mb-6">
            Add pies to compare their performance side by side.
          </p>
          <Button onClick={() => setShowAddPieModal(true)}>
            <Icon name="Plus" size="sm" className="mr-2" />
            Add First Pie
          </Button>
        </motion.div>
      )}
    </div>
  );
};

export default PieComparisonInterface;