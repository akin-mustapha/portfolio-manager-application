import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Pie } from '../../types/api';
import { Icon } from '../icons';
import { Button } from '../ui/Button';
import { containerVariants, listItemVariants, springTransition } from '../../utils/animations';

interface PieRankingTableProps {
  pies: Pie[];
  loading?: boolean;
  onPieSelect?: (pie: Pie) => void;
  selectedPie?: Pie | null;
}

type SortField = 'name' | 'totalValue' | 'returnPercentage' | 'investedAmount' | 'returnAmount' | 'positionsCount';
type SortDirection = 'asc' | 'desc';
type FilterType = 'all' | 'positive' | 'negative' | 'large' | 'small';

interface SortConfig {
  field: SortField;
  direction: SortDirection;
}

const PieRankingTable: React.FC<PieRankingTableProps> = ({
  pies,
  loading = false,
  onPieSelect,
  selectedPie
}) => {
  const [sortConfig, setSortConfig] = useState<SortConfig>({ field: 'returnPercentage', direction: 'desc' });
  const [filter, setFilter] = useState<FilterType>('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Enhanced pie data with calculated fields
  const enhancedPies = useMemo(() => {
    return pies.map(pie => ({
      ...pie,
      returnAmount: pie.returnAmount || ((pie.returnPercentage / 100) * pie.investedAmount),
      positionsCount: pie.positions?.length || 0,
      // Mock additional metrics for ranking
      volatility: Math.random() * 20 + 5,
      sharpeRatio: Math.random() * 2 + 0.5,
      maxDrawdown: -(Math.random() * 15 + 2),
      riskScore: Math.floor(Math.random() * 10) + 1
    }));
  }, [pies]);

  // Filtered and sorted pies
  const processedPies = useMemo(() => {
    let filtered = enhancedPies;

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(pie =>
        pie.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply type filter
    switch (filter) {
      case 'positive':
        filtered = filtered.filter(pie => pie.returnPercentage > 0);
        break;
      case 'negative':
        filtered = filtered.filter(pie => pie.returnPercentage < 0);
        break;
      case 'large':
        filtered = filtered.filter(pie => pie.totalValue > 10000);
        break;
      case 'small':
        filtered = filtered.filter(pie => pie.totalValue <= 10000);
        break;
    }

    // Apply sorting
    filtered.sort((a, b) => {
      const aValue = a[sortConfig.field];
      const bValue = b[sortConfig.field];
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortConfig.direction === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }
      
      const numA = Number(aValue) || 0;
      const numB = Number(bValue) || 0;
      
      return sortConfig.direction === 'asc' ? numA - numB : numB - numA;
    });

    return filtered;
  }, [enhancedPies, sortConfig, filter, searchTerm]);

  const handleSort = (field: SortField) => {
    setSortConfig(prev => ({
      field,
      direction: prev.field === field && prev.direction === 'desc' ? 'asc' : 'desc'
    }));
  };

  const getSortIcon = (field: SortField) => {
    if (sortConfig.field !== field) return 'MoreVertical';
    return sortConfig.direction === 'asc' ? 'ChevronUp' : 'ChevronDown';
  };

  const getRankBadgeColor = (rank: number) => {
    if (rank === 1) return 'bg-yellow-500 text-white';
    if (rank === 2) return 'bg-gray-400 text-white';
    if (rank === 3) return 'bg-amber-600 text-white';
    return 'bg-gray-200 text-gray-700';
  };

  const getPerformanceColor = (returnPct: number) => {
    if (returnPct > 10) return 'text-green-600 bg-green-50';
    if (returnPct > 0) return 'text-green-500 bg-green-50';
    if (returnPct > -5) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getRiskBadge = (riskScore: number) => {
    if (riskScore <= 3) return { label: 'Low', color: 'bg-green-100 text-green-800' };
    if (riskScore <= 7) return { label: 'Medium', color: 'bg-yellow-100 text-yellow-800' };
    return { label: 'High', color: 'bg-red-100 text-red-800' };
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse">
          <div className="h-10 bg-gray-200 rounded mb-4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, index) => (
              <div key={index} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Controls */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between"
      >
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Pie Rankings
          </h2>
          <p className="text-gray-600">
            {processedPies.length} of {pies.length} pies shown
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
          {/* Search */}
          <div className="relative">
            <Icon name="Search" size="sm" className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search pies..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg bg-white/80 backdrop-blur-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent w-full sm:w-64"
            />
          </div>

          {/* Filter */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as FilterType)}
            className="px-4 py-2 border border-gray-300 rounded-lg bg-white/80 backdrop-blur-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Pies</option>
            <option value="positive">Positive Returns</option>
            <option value="negative">Negative Returns</option>
            <option value="large">Large (&gt;£10k)</option>
            <option value="small">Small (≤£10k)</option>
          </select>
        </div>
      </motion.div>

      {/* Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/80 backdrop-blur-sm rounded-xl border border-gray-200 overflow-hidden"
      >
        {/* Table Header */}
        <div className="bg-gray-50/80 border-b border-gray-200">
          <div className="grid grid-cols-12 gap-4 p-4 text-sm font-medium text-gray-700">
            <div className="col-span-1 text-center">#</div>
            <div className="col-span-3">
              <button
                onClick={() => handleSort('name')}
                className="flex items-center space-x-1 hover:text-gray-900 transition-colors"
              >
                <span>Pie Name</span>
                <Icon name={getSortIcon('name')} size="xs" />
              </button>
            </div>
            <div className="col-span-2 text-right">
              <button
                onClick={() => handleSort('totalValue')}
                className="flex items-center justify-end space-x-1 hover:text-gray-900 transition-colors w-full"
              >
                <span>Total Value</span>
                <Icon name={getSortIcon('totalValue')} size="xs" />
              </button>
            </div>
            <div className="col-span-2 text-right">
              <button
                onClick={() => handleSort('returnPercentage')}
                className="flex items-center justify-end space-x-1 hover:text-gray-900 transition-colors w-full"
              >
                <span>Return %</span>
                <Icon name={getSortIcon('returnPercentage')} size="xs" />
              </button>
            </div>
            <div className="col-span-2 text-right">
              <button
                onClick={() => handleSort('returnAmount')}
                className="flex items-center justify-end space-x-1 hover:text-gray-900 transition-colors w-full"
              >
                <span>Return £</span>
                <Icon name={getSortIcon('returnAmount')} size="xs" />
              </button>
            </div>
            <div className="col-span-1 text-center">Risk</div>
            <div className="col-span-1 text-center">
              <button
                onClick={() => handleSort('positionsCount')}
                className="flex items-center justify-center space-x-1 hover:text-gray-900 transition-colors w-full"
              >
                <span>Pos.</span>
                <Icon name={getSortIcon('positionsCount')} size="xs" />
              </button>
            </div>
          </div>
        </div>

        {/* Table Body */}
        <motion.div variants={containerVariants} initial="initial" animate="animate">
          <AnimatePresence>
            {processedPies.map((pie, index) => {
              const rank = index + 1;
              const isSelected = selectedPie?.id === pie.id;
              const riskBadge = getRiskBadge(pie.riskScore);
              
              return (
                <motion.div
                  key={pie.id}
                  variants={listItemVariants}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  layout
                  transition={springTransition}
                  className={`
                    grid grid-cols-12 gap-4 p-4 border-b border-gray-100 hover:bg-blue-50/50 cursor-pointer transition-all duration-200
                    ${isSelected ? 'bg-blue-100/50 border-blue-200' : ''}
                  `}
                  onClick={() => onPieSelect?.(pie)}
                  whileHover={{ scale: 1.005 }}
                  whileTap={{ scale: 0.995 }}
                >
                  {/* Rank */}
                  <div className="col-span-1 flex justify-center">
                    <motion.div
                      className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${getRankBadgeColor(rank)}`}
                      whileHover={{ scale: 1.1 }}
                    >
                      {rank}
                    </motion.div>
                  </div>

                  {/* Pie Name */}
                  <div className="col-span-3">
                    <div className="font-medium text-gray-900 truncate">{pie.name}</div>
                    <div className="text-sm text-gray-500">
                      Updated {new Date(pie.updatedAt).toLocaleDateString()}
                    </div>
                  </div>

                  {/* Total Value */}
                  <div className="col-span-2 text-right">
                    <div className="font-medium text-gray-900">
                      £{pie.totalValue.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-500">
                      £{pie.investedAmount.toLocaleString()} invested
                    </div>
                  </div>

                  {/* Return Percentage */}
                  <div className="col-span-2 text-right">
                    <motion.div
                      className={`inline-flex items-center px-2 py-1 rounded-full text-sm font-medium ${getPerformanceColor(pie.returnPercentage)}`}
                      whileHover={{ scale: 1.05 }}
                    >
                      <Icon 
                        name={pie.returnPercentage >= 0 ? 'TrendingUp' : 'TrendingDown'} 
                        size="xs" 
                        className="mr-1" 
                      />
                      {pie.returnPercentage.toFixed(2)}%
                    </motion.div>
                  </div>

                  {/* Return Amount */}
                  <div className="col-span-2 text-right">
                    <div className={`font-medium ${pie.returnAmount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {pie.returnAmount >= 0 ? '+' : ''}£{Math.abs(pie.returnAmount).toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-500">
                      {((pie.returnAmount / pie.investedAmount) * 100).toFixed(1)}% of invested
                    </div>
                  </div>

                  {/* Risk */}
                  <div className="col-span-1 flex justify-center">
                    <motion.span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${riskBadge.color}`}
                      whileHover={{ scale: 1.05 }}
                    >
                      {riskBadge.label}
                    </motion.span>
                  </div>

                  {/* Positions Count */}
                  <div className="col-span-1 text-center">
                    <div className="font-medium text-gray-900">{pie.positionsCount}</div>
                    <div className="text-xs text-gray-500">holdings</div>
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </motion.div>

        {/* Empty State */}
        {processedPies.length === 0 && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-12"
          >
            <div className="text-gray-400 mb-4">
              <Icon name="Search" size="2xl" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No Pies Found
            </h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || filter !== 'all' 
                ? 'Try adjusting your search or filter criteria.'
                : 'No pies available to display.'
              }
            </p>
            {(searchTerm || filter !== 'all') && (
              <Button
                variant="outline"
                onClick={() => {
                  setSearchTerm('');
                  setFilter('all');
                }}
              >
                Clear Filters
              </Button>
            )}
          </motion.div>
        )}
      </motion.div>

      {/* Summary Stats */}
      {processedPies.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-4"
        >
          <div className="bg-white/80 backdrop-blur-sm rounded-lg p-4 border border-gray-200">
            <div className="text-2xl font-bold text-gray-900">
              {processedPies.length}
            </div>
            <div className="text-sm text-gray-600">Total Pies</div>
          </div>
          
          <div className="bg-white/80 backdrop-blur-sm rounded-lg p-4 border border-gray-200">
            <div className="text-2xl font-bold text-green-600">
              {processedPies.filter(p => p.returnPercentage > 0).length}
            </div>
            <div className="text-sm text-gray-600">Profitable</div>
          </div>
          
          <div className="bg-white/80 backdrop-blur-sm rounded-lg p-4 border border-gray-200">
            <div className="text-2xl font-bold text-blue-600">
              £{processedPies.reduce((sum, pie) => sum + pie.totalValue, 0).toLocaleString()}
            </div>
            <div className="text-sm text-gray-600">Total Value</div>
          </div>
          
          <div className="bg-white/80 backdrop-blur-sm rounded-lg p-4 border border-gray-200">
            <div className="text-2xl font-bold text-purple-600">
              {(processedPies.reduce((sum, pie) => sum + pie.returnPercentage, 0) / processedPies.length).toFixed(2)}%
            </div>
            <div className="text-sm text-gray-600">Avg Return</div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default PieRankingTable;