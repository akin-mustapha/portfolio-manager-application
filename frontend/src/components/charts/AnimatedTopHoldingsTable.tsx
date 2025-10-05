import React, { useState, useMemo, useRef } from 'react';
import { motion, AnimatePresence, useInView } from 'framer-motion';
import { Icon } from '../icons';
import { AssetType } from '../../types';
import { 
  springTransition, 
  smoothTransition,
  staggerConfigs,
  hoverVariants
} from '../../utils/animations';

export interface HoldingData {
  symbol: string;
  name: string;
  value: number;
  percentage: number;
  quantity: number;
  currentPrice: number;
  change: number;
  changePercentage: number;
  sector?: string;
  country?: string;
  assetType?: 'STOCK' | 'ETF' | 'CRYPTO';
}

type SortField = 'value' | 'percentage' | 'change' | 'changePercentage' | 'name' | 'symbol';
type SortDirection = 'asc' | 'desc';

interface AnimatedTopHoldingsTableProps {
  data: HoldingData[];
  title?: string;
  maxRows?: number;
  loading?: boolean;
  showSearch?: boolean;
  showFilters?: boolean;
  animationDelay?: number;
  onRowClick?: (holding: HoldingData) => void;
  className?: string;
}

// Sort configuration
interface SortConfig {
  field: SortField;
  direction: SortDirection;
}

// Filter configuration
interface FilterConfig {
  sector?: string;
  assetType?: string;
  minValue?: number;
  maxValue?: number;
}

// Table header configuration
const TABLE_HEADERS = [
  { key: 'symbol' as SortField, label: 'Symbol', sortable: true, width: 'w-20' },
  { key: 'name' as SortField, label: 'Name', sortable: true, width: 'flex-1' },
  { key: 'value' as SortField, label: 'Value', sortable: true, width: 'w-24' },
  { key: 'percentage' as SortField, label: 'Weight', sortable: true, width: 'w-20' },
  { key: 'change' as SortField, label: 'Change', sortable: true, width: 'w-24' },
  { key: 'changePercentage' as SortField, label: 'Change %', sortable: true, width: 'w-20' },
];

// Loading skeleton row
const SkeletonRow: React.FC<{ index: number }> = ({ index }) => (
  <motion.tr
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: index * 0.05, ...smoothTransition }}
    className="border-b border-gray-100 dark:border-gray-700"
  >
    {TABLE_HEADERS.map((header, colIndex) => (
      <td key={colIndex} className={`px-4 py-3 ${header.width}`}>
        <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </td>
    ))}
  </motion.tr>
);

// Table header component with sorting
const TableHeader: React.FC<{
  sortConfig: SortConfig;
  onSort: (field: SortField) => void;
  isVisible: boolean;
  delay: number;
}> = ({ sortConfig, onSort, isVisible, delay }) => (
  <motion.thead
    initial={{ opacity: 0, y: -10 }}
    animate={{ opacity: isVisible ? 1 : 0, y: isVisible ? 0 : -10 }}
    transition={{ delay, ...smoothTransition }}
    className="bg-gray-50 dark:bg-gray-800/50"
  >
    <tr>
      {TABLE_HEADERS.map((header, index) => (
        <motion.th
          key={header.key}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: isVisible ? 1 : 0, x: isVisible ? 0 : -10 }}
          transition={{ delay: delay + index * 0.05, ...smoothTransition }}
          className={`px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider ${header.width} ${
            header.sortable ? 'cursor-pointer hover:text-gray-700 dark:hover:text-gray-200' : ''
          }`}
          onClick={() => header.sortable && onSort(header.key)}
          whileHover={header.sortable ? { scale: 1.02 } : undefined}
        >
          <div className="flex items-center space-x-1">
            <span>{header.label}</span>
            {header.sortable && (
              <motion.div
                animate={{
                  rotate: sortConfig.field === header.key && sortConfig.direction === 'desc' ? 180 : 0
                }}
                transition={springTransition}
              >
                <Icon 
                  name="ChevronUp" 
                  size="sm" 
                  className={`transition-colors ${
                    sortConfig.field === header.key 
                      ? 'text-primary-500' 
                      : 'text-gray-400'
                  }`}
                />
              </motion.div>
            )}
          </div>
        </motion.th>
      ))}
    </tr>
  </motion.thead>
);

// Table row component with animations
const TableRow: React.FC<{
  holding: HoldingData;
  index: number;
  isVisible: boolean;
  delay: number;
  onClick?: (holding: HoldingData) => void;
}> = ({ holding, index, isVisible, delay, onClick }) => {
  const isPositiveChange = holding.changePercentage >= 0;

  return (
    <motion.tr
      initial={{ opacity: 0, y: 20 }}
      animate={{ 
        opacity: isVisible ? 1 : 0, 
        y: isVisible ? 0 : 20 
      }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ delay: delay + index * 0.05, ...smoothTransition }}
      className={`border-b border-gray-100 dark:border-gray-700 transition-colors duration-200 ${
        onClick 
          ? 'hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer' 
          : ''
      }`}
      onClick={() => onClick?.(holding)}
      whileHover={onClick ? { scale: 1.01, x: 2 } : undefined}
      whileTap={onClick ? { scale: 0.99 } : undefined}
    >
      {/* Symbol */}
      <td className="px-4 py-3 w-20">
        <motion.div 
          className="flex items-center"
          whileHover={{ scale: 1.05 }}
        >
          <span className="font-mono text-sm font-medium text-gray-900 dark:text-white">
            {holding.symbol}
          </span>
          {holding.assetType && (
            <span className={`ml-2 px-1.5 py-0.5 text-xs rounded-full ${
              holding.assetType === 'ETF' 
                ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                : holding.assetType === 'CRYPTO'
                ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'
                : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
            }`}>
              {holding.assetType}
            </span>
          )}
        </motion.div>
      </td>

      {/* Name */}
      <td className="px-4 py-3 flex-1">
        <div className="min-w-0">
          <p className="text-sm font-medium text-gray-900 dark:text-white truncate" title={holding.name}>
            {holding.name}
          </p>
          {holding.sector && (
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
              {holding.sector}
              {holding.country && ` • ${holding.country}`}
            </p>
          )}
        </div>
      </td>

      {/* Value */}
      <td className="px-4 py-3 w-24">
        <div className="text-right">
          <p className="text-sm font-medium text-gray-900 dark:text-white">
            £{holding.value.toLocaleString()}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {holding.quantity.toLocaleString()} @ £{holding.currentPrice.toFixed(2)}
          </p>
        </div>
      </td>

      {/* Weight */}
      <td className="px-4 py-3 w-20">
        <div className="text-right">
          <span className="text-sm font-medium text-gray-900 dark:text-white">
            {holding.percentage.toFixed(1)}%
          </span>
          {/* Visual weight bar */}
          <div className="mt-1 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1">
            <motion.div
              className="bg-primary-500 h-1 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(holding.percentage * 2, 100)}%` }}
              transition={{ delay: delay + index * 0.05 + 0.3, duration: 0.8, ease: 'easeOut' }}
            />
          </div>
        </div>
      </td>

      {/* Change */}
      <td className="px-4 py-3 w-24">
        <div className="text-right">
          <motion.p 
            className={`text-sm font-medium flex items-center justify-end ${
              isPositiveChange 
                ? 'text-green-600 dark:text-green-400' 
                : 'text-red-600 dark:text-red-400'
            }`}
            whileHover={{ scale: 1.05 }}
          >
            <Icon 
              name={isPositiveChange ? 'TrendingUp' : 'TrendingDown'} 
              size="sm" 
              className="mr-1"
            />
            £{Math.abs(holding.change).toFixed(2)}
          </motion.p>
        </div>
      </td>

      {/* Change % */}
      <td className="px-4 py-3 w-20">
        <div className="text-right">
          <motion.span 
            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
              isPositiveChange
                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
            }`}
            whileHover={{ scale: 1.05 }}
            transition={springTransition}
          >
            {isPositiveChange ? '+' : ''}{holding.changePercentage.toFixed(2)}%
          </motion.span>
        </div>
      </td>
    </motion.tr>
  );
};

// Search and filter component
const SearchAndFilters: React.FC<{
  searchTerm: string;
  onSearchChange: (term: string) => void;
  filterConfig: FilterConfig;
  onFilterChange: (config: FilterConfig) => void;
  sectors: string[];
  assetTypes: string[];
  isVisible: boolean;
  delay: number;
}> = ({ 
  searchTerm, 
  onSearchChange, 
  filterConfig, 
  onFilterChange, 
  sectors, 
  assetTypes,
  isVisible,
  delay
}) => (
  <motion.div
    initial={{ opacity: 0, y: -10 }}
    animate={{ opacity: isVisible ? 1 : 0, y: isVisible ? 0 : -10 }}
    transition={{ delay, ...smoothTransition }}
    className="mb-4 space-y-3"
  >
    {/* Search */}
    <div className="relative">
      <Icon 
        name="Search" 
        size="sm" 
        className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
      />
      <input
        type="text"
        placeholder="Search holdings..."
        value={searchTerm}
        onChange={(e) => onSearchChange(e.target.value)}
        className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
      />
    </div>

    {/* Filters */}
    <div className="flex flex-wrap gap-3">
      {/* Sector filter */}
      <select
        value={filterConfig.sector || ''}
        onChange={(e) => onFilterChange({ ...filterConfig, sector: e.target.value || undefined })}
        className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
      >
        <option value="">All Sectors</option>
        {sectors.map(sector => (
          <option key={sector} value={sector}>{sector}</option>
        ))}
      </select>

      {/* Asset type filter */}
      <select
        value={filterConfig.assetType || ''}
        onChange={(e) => onFilterChange({ ...filterConfig, assetType: e.target.value || undefined })}
        className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
      >
        <option value="">All Types</option>
        {assetTypes.map(type => (
          <option key={type} value={type}>{type}</option>
        ))}
      </select>

      {/* Clear filters */}
      {(filterConfig.sector || filterConfig.assetType || searchTerm) && (
        <motion.button
          onClick={() => {
            onFilterChange({});
            onSearchChange('');
          }}
          className="px-3 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          Clear filters
        </motion.button>
      )}
    </div>
  </motion.div>
);

const AnimatedTopHoldingsTable: React.FC<AnimatedTopHoldingsTableProps> = ({
  data,
  title = "Top Holdings",
  maxRows = 10,
  loading = false,
  showSearch = true,
  showFilters = true,
  animationDelay = 0,
  onRowClick,
  className = ''
}) => {
  const [sortConfig, setSortConfig] = useState<SortConfig>({ field: 'value', direction: 'desc' });
  const [searchTerm, setSearchTerm] = useState('');
  const [filterConfig, setFilterConfig] = useState<FilterConfig>({});
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });

  // Get unique sectors and asset types for filters
  const { sectors, assetTypes } = useMemo(() => {
    const sectors = Array.from(new Set(data.map(item => item.sector).filter((sector): sector is string => Boolean(sector)))).sort();
    const assetTypes = Array.from(new Set(data.map(item => item.assetType).filter((type): type is AssetType => Boolean(type)).map(type => type.toString()))).sort();
    return { sectors, assetTypes };
  }, [data]);

  // Sort and filter data
  const processedData = useMemo(() => {
    let filtered = data;

    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(item => 
        item.name.toLowerCase().includes(term) ||
        item.symbol.toLowerCase().includes(term) ||
        item.sector?.toLowerCase().includes(term)
      );
    }

    // Apply filters
    if (filterConfig.sector) {
      filtered = filtered.filter(item => item.sector === filterConfig.sector);
    }
    if (filterConfig.assetType) {
      filtered = filtered.filter(item => item.assetType === filterConfig.assetType);
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
      
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortConfig.direction === 'asc' 
          ? aValue - bValue
          : bValue - aValue;
      }
      
      return 0;
    });

    return filtered.slice(0, maxRows);
  }, [data, sortConfig, searchTerm, filterConfig, maxRows]);

  // Handle sorting
  const handleSort = (field: SortField) => {
    setSortConfig(prev => ({
      field,
      direction: prev.field === field && prev.direction === 'desc' ? 'asc' : 'desc'
    }));
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
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          {title}
        </h3>
        
        <div className="overflow-hidden">
          <table className="min-w-full">
            <TableHeader
              sortConfig={sortConfig}
              onSort={handleSort}
              isVisible={true}
              delay={0}
            />
            <tbody>
              {[...Array(maxRows)].map((_, index) => (
                <SkeletonRow key={index} index={index} />
              ))}
            </tbody>
          </table>
        </div>
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
            <Icon name="BarChart" size="2xl" />
          </div>
          <p className="text-gray-500 font-medium">No holdings data available</p>
          <p className="text-gray-400 text-sm mt-1">
            Holdings will appear when portfolio is loaded
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
        className="flex items-center justify-between mb-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: isInView ? 1 : 0 }}
        transition={{ delay: animationDelay + 0.2, duration: 0.5 }}
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          {title}
        </h3>
        <div className="text-sm text-gray-500 dark:text-gray-400">
          {processedData.length} of {data.length} holdings
        </div>
      </motion.div>

      {/* Search and Filters */}
      {(showSearch || showFilters) && (
        <SearchAndFilters
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          filterConfig={filterConfig}
          onFilterChange={setFilterConfig}
          sectors={sectors}
          assetTypes={assetTypes}
          isVisible={isInView}
          delay={animationDelay + 0.3}
        />
      )}

      {/* Table */}
      <motion.div
        className="overflow-x-auto"
        initial={{ opacity: 0 }}
        animate={{ opacity: isInView ? 1 : 0 }}
        transition={{ delay: animationDelay + 0.4, duration: 0.5 }}
      >
        <table className="min-w-full">
          <TableHeader
            sortConfig={sortConfig}
            onSort={handleSort}
            isVisible={isInView}
            delay={animationDelay + 0.5}
          />
          
          <motion.tbody
            variants={staggerConfigs.container}
            initial="initial"
            animate={isInView ? "animate" : "initial"}
          >
            <AnimatePresence mode="popLayout">
              {processedData.map((holding, index) => (
                <TableRow
                  key={`${holding.symbol}-${index}`}
                  holding={holding}
                  index={index}
                  isVisible={isInView}
                  delay={animationDelay + 0.6}
                  onClick={onRowClick}
                />
              ))}
            </AnimatePresence>
          </motion.tbody>
        </table>
      </motion.div>

      {/* Summary */}
      <motion.div 
        className="border-t border-gray-200 dark:border-gray-700 pt-4 mt-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: isInView ? 1 : 0 }}
        transition={{ delay: animationDelay + 1, duration: 0.5 }}
      >
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">
            Total Value (Top {processedData.length})
          </span>
          <span className="font-medium text-gray-900 dark:text-white">
            £{processedData.reduce((sum, item) => sum + item.value, 0).toLocaleString()}
          </span>
        </div>
        
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
          <span>
            {processedData.reduce((sum, item) => sum + item.percentage, 0).toFixed(1)}% of portfolio
          </span>
          <span>
            Live data
          </span>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default AnimatedTopHoldingsTable;