import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../services/api';
import { Pie } from '../types/api';
import PiePerformanceDashboard from '../components/pie/PiePerformanceDashboard';
import PieComparisonInterface from '../components/pie/PieComparisonInterface';
import PieRankingTable from '../components/pie/PieRankingTable';
import PieAllocationBreakdown from '../components/pie/PieAllocationBreakdown';
import PiePerformanceTimeline from '../components/pie/PiePerformanceTimeline';
import { Icon } from '../components/icons';
import { Button } from '../components/ui/Button';
import { containerVariants, listItemVariants } from '../utils/animations';

type ViewMode = 'dashboard' | 'comparison' | 'ranking' | 'allocation' | 'timeline';

const PieAnalysis: React.FC = () => {
  const [selectedPie, setSelectedPie] = useState<Pie | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('dashboard');
  const [comparisonPies, setComparisonPies] = useState<Pie[]>([]);

  // Fetch pies data
  const { data: pies = [], isLoading, error } = useQuery({
    queryKey: ['pies'],
    queryFn: apiService.getPies,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Set default selected pie when data loads
  useEffect(() => {
    if (pies.length > 0 && !selectedPie) {
      setSelectedPie(pies[0]);
    }
  }, [pies, selectedPie]);

  const viewModeConfig = {
    dashboard: {
      title: 'Pie Performance Dashboard',
      icon: 'BarChart',
      description: 'Comprehensive performance metrics for your selected pie'
    },
    comparison: {
      title: 'Pie Comparison',
      icon: 'BarChart3',
      description: 'Compare performance across multiple pies'
    },
    ranking: {
      title: 'Pie Rankings',
      icon: 'TrendingUp',
      description: 'Ranked performance analysis of all pies'
    },
    allocation: {
      title: 'Allocation Breakdown',
      icon: 'PieChart',
      description: 'Detailed allocation analysis with drill-down capabilities'
    },
    timeline: {
      title: 'Performance Timeline',
      icon: 'LineChart',
      description: 'Interactive timeline with historical performance'
    }
  };

  const handlePieSelect = (pie: Pie) => {
    setSelectedPie(pie);
    if (viewMode === 'comparison') {
      // Add to comparison if not already included
      if (!comparisonPies.find(p => p.id === pie.id)) {
        setComparisonPies(prev => [...prev, pie].slice(0, 4)); // Max 4 pies for comparison
      }
    }
  };

  const handleViewModeChange = (mode: ViewMode) => {
    setViewMode(mode);
    if (mode === 'comparison' && selectedPie && comparisonPies.length === 0) {
      setComparisonPies([selectedPie]);
    }
  };

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="min-h-screen flex items-center justify-center"
      >
        <div className="text-center">
          <div className="text-red-500 mb-4">
            <Icon name="AlertCircle" size="2xl" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Failed to Load Pie Data</h2>
          <p className="text-gray-600 mb-4">
            {error instanceof Error ? error.message : 'An unexpected error occurred'}
          </p>
          <Button onClick={() => window.location.reload()}>
            <Icon name="Refresh" size="sm" className="mr-2" />
            Retry
          </Button>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial="initial"
      animate="animate"
      variants={containerVariants}
      className="space-y-6 p-6"
    >
      {/* Header Section */}
      <motion.div variants={listItemVariants} className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Pie Analysis
            </h1>
            <p className="text-gray-600">
              {viewModeConfig[viewMode].description}
            </p>
          </div>
          
          {/* Pie Selector */}
          {pies.length > 0 && (
            <div className="flex items-center space-x-4">
              <select
                value={selectedPie?.id || ''}
                onChange={(e) => {
                  const pie = pies.find(p => p.id === e.target.value);
                  if (pie) handlePieSelect(pie);
                }}
                className="px-4 py-2 border border-gray-300 rounded-lg bg-white/80 backdrop-blur-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select a pie...</option>
                {pies.map((pie) => (
                  <option key={pie.id} value={pie.id}>
                    {pie.name} (£{pie.totalValue.toLocaleString()})
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* View Mode Navigation */}
        <div className="flex flex-wrap gap-2">
          {(Object.keys(viewModeConfig) as ViewMode[]).map((mode) => (
            <motion.button
              key={mode}
              onClick={() => handleViewModeChange(mode)}
              className={`
                flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200
                ${viewMode === mode
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-white/80 text-gray-700 hover:bg-blue-50 border border-gray-200'
                }
              `}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Icon name={viewModeConfig[mode].icon as any} size="sm" />
              <span>{viewModeConfig[mode].title}</span>
            </motion.button>
          ))}
        </div>
      </motion.div>

      {/* Main Content Area */}
      <AnimatePresence mode="wait">
        <motion.div
          key={viewMode}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
          className="min-h-[600px]"
        >
          {viewMode === 'dashboard' && (
            <PiePerformanceDashboard
              pie={selectedPie}
              loading={isLoading}
              onPieSelect={handlePieSelect}
              availablePies={pies}
            />
          )}

          {viewMode === 'comparison' && (
            <PieComparisonInterface
              selectedPies={comparisonPies}
              availablePies={pies}
              loading={isLoading}
              onPieAdd={(pie) => setComparisonPies(prev => [...prev, pie].slice(0, 4))}
              onPieRemove={(pieId) => setComparisonPies(prev => prev.filter(p => p.id !== pieId))}
            />
          )}

          {viewMode === 'ranking' && (
            <PieRankingTable
              pies={pies}
              loading={isLoading}
              onPieSelect={handlePieSelect}
              selectedPie={selectedPie}
            />
          )}

          {viewMode === 'allocation' && (
            <PieAllocationBreakdown
              pie={selectedPie}
              loading={isLoading}
              onPositionClick={(position) => console.log('Position clicked:', position)}
            />
          )}

          {viewMode === 'timeline' && (
            <PiePerformanceTimeline
              pie={selectedPie}
              loading={isLoading}
              onTimeRangeChange={(range) => console.log('Time range changed:', range)}
            />
          )}
        </motion.div>
      </AnimatePresence>

      {/* Empty State */}
      {!isLoading && pies.length === 0 && (
        <motion.div
          variants={listItemVariants}
          className="text-center py-12"
        >
          <div className="text-gray-400 mb-4">
            <Icon name="PieChart" size="2xl" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            No Pies Found
          </h3>
          <p className="text-gray-600 mb-6">
            Create pies in your Trading 212 account to see detailed analysis here.
          </p>
          <Button variant="outline">
            <Icon name="Refresh" size="sm" className="mr-2" />
            Refresh Data
          </Button>
        </motion.div>
      )}
    </motion.div>
  );
};

export default PieAnalysis;