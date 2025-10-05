import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PieChart, Pie as RechartsPie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis } from 'recharts';
import { Pie, Position } from '../../types/api';
import { Icon } from '../icons';
import { Button } from '../ui/Button';
import { containerVariants, listItemVariants, springTransition } from '../../utils/animations';

interface PieAllocationBreakdownProps {
  pie: Pie | null;
  loading?: boolean;
  onPositionClick?: (position: Position) => void;
}

type ViewMode = 'overview' | 'sectors' | 'countries' | 'assets' | 'positions';
type ChartType = 'pie' | 'bar' | 'treemap';

interface AllocationData {
  name: string;
  value: number;
  percentage: number;
  count: number;
  color: string;
  positions?: Position[];
  [key: string]: any;
}

const PieAllocationBreakdown: React.FC<PieAllocationBreakdownProps> = ({
  pie,
  loading = false,
  onPositionClick
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>('overview');
  const [chartType, setChartType] = useState<ChartType>('pie');
  const [selectedSegment, setSelectedSegment] = useState<string | null>(null);
  const [drillDownLevel, setDrillDownLevel] = useState(0);
  const [breadcrumb, setBreadcrumb] = useState<string[]>([]);

  // Color palette for charts
  const colors = [
    '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
    '#06B6D4', '#F97316', '#84CC16', '#EC4899', '#6366F1',
    '#14B8A6', '#F43F5E', '#8B5A2B', '#6B7280', '#9CA3AF'
  ];

  // Mock enhanced position data with sectors, countries, etc.
  const enhancedPositions = useMemo(() => {
    if (!pie?.positions) return [];
    
    return pie.positions.map((position, index) => ({
      ...position,
      sector: position.sector || ['Technology', 'Healthcare', 'Finance', 'Consumer', 'Energy', 'Materials'][index % 6],
      country: position.country || ['USA', 'UK', 'Germany', 'Japan', 'Canada', 'France'][index % 6],
      assetType: position.assetType || (['STOCK', 'ETF', 'CRYPTO'] as const)[index % 3],
      industry: position.industry || ['Software', 'Pharmaceuticals', 'Banking', 'Retail', 'Oil & Gas', 'Mining'][index % 6],
      weight: (position.marketValue / pie.totalValue) * 100
    }));
  }, [pie]);

  // Generate allocation data based on view mode
  const allocationData = useMemo((): AllocationData[] => {
    if (!enhancedPositions.length) return [];

    const groupBy = (key: keyof typeof enhancedPositions[0]) => {
      const groups = enhancedPositions.reduce((acc, position) => {
        const groupKey = String(position[key]);
        if (!acc[groupKey]) {
          acc[groupKey] = {
            name: groupKey,
            value: 0,
            count: 0,
            positions: []
          };
        }
        acc[groupKey].value += position.marketValue;
        acc[groupKey].count += 1;
        acc[groupKey].positions.push(position);
        return acc;
      }, {} as Record<string, { name: string; value: number; count: number; positions: Position[] }>);

      return Object.values(groups)
        .map((group, index) => ({
          ...group,
          percentage: (group.value / pie!.totalValue) * 100,
          color: colors[index % colors.length]
        }))
        .sort((a, b) => b.value - a.value);
    };

    switch (viewMode) {
      case 'sectors':
        return groupBy('sector');
      case 'countries':
        return groupBy('country');
      case 'assets':
        return groupBy('assetType');
      case 'positions':
        return enhancedPositions
          .map((position, index) => ({
            name: position.name,
            value: position.marketValue,
            percentage: position.weight,
            count: 1,
            color: colors[index % colors.length],
            positions: [position]
          }))
          .sort((a, b) => b.value - a.value)
          .slice(0, 20); // Show top 20 positions
      default:
        return [
          {
            name: 'Total Portfolio',
            value: pie!.totalValue,
            percentage: 100,
            count: enhancedPositions.length,
            color: colors[0],
            positions: enhancedPositions
          }
        ];
    }
  }, [enhancedPositions, viewMode, pie]);

  const handleSegmentClick = (data: AllocationData) => {
    if (viewMode === 'positions' && data.positions?.[0]) {
      onPositionClick?.(data.positions[0]);
      return;
    }

    // Drill down functionality
    if (data.positions && data.positions.length > 1) {
      setSelectedSegment(data.name);
      setBreadcrumb(prev => [...prev, data.name]);
      setDrillDownLevel(prev => prev + 1);
      
      // Switch to positions view for drill-down
      if (viewMode !== 'positions') {
        setViewMode('positions');
      }
    }
  };

  const handleBreadcrumbClick = (index: number) => {
    setBreadcrumb(prev => prev.slice(0, index + 1));
    setDrillDownLevel(index + 1);
    if (index === 0) {
      setSelectedSegment(null);
    }
  };

  const resetDrillDown = () => {
    setSelectedSegment(null);
    setBreadcrumb([]);
    setDrillDownLevel(0);
    setViewMode('overview');
  };

  const viewModeConfig = {
    overview: { label: 'Overview', icon: 'PieChart' },
    sectors: { label: 'Sectors', icon: 'BarChart' },
    countries: { label: 'Countries', icon: 'Globe' },
    assets: { label: 'Asset Types', icon: 'Database' },
    positions: { label: 'Positions', icon: 'Target' }
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white/95 backdrop-blur-md border border-gray-200 rounded-lg shadow-lg p-3"
        >
          <p className="font-medium text-gray-900">{data.name}</p>
          <p className="text-sm text-gray-600">
            Value: £{data.value.toLocaleString()}
          </p>
          <p className="text-sm text-gray-600">
            Weight: {data.percentage.toFixed(2)}%
          </p>
          <p className="text-sm text-gray-600">
            Holdings: {data.count}
          </p>
        </motion.div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!pie) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-12"
      >
        <div className="text-gray-400 mb-4">
          <Icon name="PieChart" size="2xl" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Select a Pie to View Allocation
        </h3>
        <p className="text-gray-600">
          Choose a pie to see its detailed allocation breakdown.
        </p>
      </motion.div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4"
      >
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Allocation Breakdown: {pie.name}
          </h2>
          
          {/* Breadcrumb */}
          {breadcrumb.length > 0 && (
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <button
                onClick={resetDrillDown}
                className="hover:text-blue-600 transition-colors"
              >
                Portfolio
              </button>
              {breadcrumb.map((crumb, index) => (
                <React.Fragment key={index}>
                  <Icon name="ChevronRight" size="xs" />
                  <button
                    onClick={() => handleBreadcrumbClick(index)}
                    className="hover:text-blue-600 transition-colors"
                  >
                    {crumb}
                  </button>
                </React.Fragment>
              ))}
            </div>
          )}
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          {/* View Mode Selector */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            {(Object.keys(viewModeConfig) as ViewMode[]).map((mode) => (
              <motion.button
                key={mode}
                onClick={() => setViewMode(mode)}
                className={`
                  flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200
                  ${viewMode === mode
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                  }
                `}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Icon name={viewModeConfig[mode].icon as any} size="xs" />
                <span className="hidden sm:inline">{viewModeConfig[mode].label}</span>
              </motion.button>
            ))}
          </div>

          {/* Chart Type Selector */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <motion.button
              onClick={() => setChartType('pie')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                chartType === 'pie' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600'
              }`}
              whileHover={{ scale: 1.02 }}
            >
              <Icon name="PieChart" size="sm" />
            </motion.button>
            <motion.button
              onClick={() => setChartType('bar')}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                chartType === 'bar' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-600'
              }`}
              whileHover={{ scale: 1.02 }}
            >
              <Icon name="BarChart" size="sm" />
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-2 bg-white/80 backdrop-blur-sm rounded-xl p-6 border border-gray-200"
        >
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              {chartType === 'pie' ? (
                <PieChart>
                  <RechartsPie
                    data={allocationData}
                    cx="50%"
                    cy="50%"
                    outerRadius={120}
                    innerRadius={40}
                    paddingAngle={2}
                    dataKey="value"
                    animationBegin={0}
                    animationDuration={800}
                  >
                    {allocationData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={entry.color}
                        stroke="white"
                        strokeWidth={2}
                        style={{ cursor: 'pointer' }}
                        onClick={() => handleSegmentClick(entry)}
                      />
                    ))}
                  </RechartsPie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              ) : (
                <BarChart data={allocationData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <XAxis 
                    dataKey="name" 
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    fontSize={12}
                  />
                  <YAxis 
                    tickFormatter={(value) => `£${(value / 1000).toFixed(0)}k`}
                    fontSize={12}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar 
                    dataKey="value" 
                    radius={[4, 4, 0, 0]}
                    style={{ cursor: 'pointer' }}
                    onClick={(data: any) => {
                      const allocationItem = allocationData.find(item => item.name === data.payload?.name);
                      if (allocationItem) handleSegmentClick(allocationItem);
                    }}
                  >
                    {allocationData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              )}
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Legend & Details */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="space-y-4"
        >
          {/* Summary Card */}
          <div className="bg-white/80 backdrop-blur-sm rounded-xl p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Summary</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Value:</span>
                <span className="font-medium">£{pie.totalValue.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total Positions:</span>
                <span className="font-medium">{enhancedPositions.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">View:</span>
                <span className="font-medium">{viewModeConfig[viewMode].label}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Segments:</span>
                <span className="font-medium">{allocationData.length}</span>
              </div>
            </div>
          </div>

          {/* Legend */}
          <div className="bg-white/80 backdrop-blur-sm rounded-xl p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Breakdown</h3>
            <motion.div 
              variants={containerVariants}
              initial="initial"
              animate="animate"
              className="space-y-2 max-h-80 overflow-y-auto"
            >
              <AnimatePresence>
                {allocationData.map((item, index) => (
                  <motion.div
                    key={item.name}
                    variants={listItemVariants}
                    initial="initial"
                    animate="animate"
                    exit="exit"
                    layout
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-all duration-200"
                    onClick={() => handleSegmentClick(item)}
                    whileHover={{ scale: 1.02, x: 4 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="flex items-center space-x-3">
                      <div
                        className="w-4 h-4 rounded-full"
                        style={{ backgroundColor: item.color }}
                      />
                      <div>
                        <div className="font-medium text-gray-900 text-sm">
                          {item.name}
                        </div>
                        <div className="text-xs text-gray-500">
                          {item.count} holding{item.count !== 1 ? 's' : ''}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium text-gray-900 text-sm">
                        {item.percentage.toFixed(1)}%
                      </div>
                      <div className="text-xs text-gray-500">
                        £{(item.value / 1000).toFixed(0)}k
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </motion.div>
          </div>

          {/* Actions */}
          <div className="bg-white/80 backdrop-blur-sm rounded-xl p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
            <div className="space-y-2">
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => console.log('Export allocation data')}
              >
                <Icon name="Download" size="sm" className="mr-2" />
                Export Data
              </Button>
              
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => console.log('View rebalancing suggestions')}
              >
                <Icon name="Target" size="sm" className="mr-2" />
                Rebalancing
              </Button>
              
              {breadcrumb.length > 0 && (
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={resetDrillDown}
                >
                  <Icon name="ArrowLeft" size="sm" className="mr-2" />
                  Back to Overview
                </Button>
              )}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Detailed Table for Positions View */}
      {viewMode === 'positions' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white/80 backdrop-blur-sm rounded-xl border border-gray-200 overflow-hidden"
        >
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Position Details</h3>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50/80">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Position
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Value
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Weight
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    P&L
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sector
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                <AnimatePresence>
                  {allocationData.slice(0, 10).map((item, index) => {
                    const position = item.positions?.[0];
                    if (!position) return null;
                    
                    return (
                      <motion.tr
                        key={position.symbol}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        transition={{ delay: index * 0.05 }}
                        className="hover:bg-gray-50 cursor-pointer"
                        onClick={() => onPositionClick?.(position)}
                      >
                        <td className="px-6 py-4">
                          <div>
                            <div className="font-medium text-gray-900">{position.name}</div>
                            <div className="text-sm text-gray-500">{position.symbol}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="font-medium text-gray-900">
                            £{position.marketValue.toLocaleString()}
                          </div>
                          <div className="text-sm text-gray-500">
                            {position.quantity} @ £{position.currentPrice.toFixed(2)}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className="font-medium text-gray-900">
                            {item.percentage.toFixed(2)}%
                          </div>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <div className={`font-medium ${
                            position.unrealizedPnl >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {position.unrealizedPnl >= 0 ? '+' : ''}£{position.unrealizedPnl.toLocaleString()}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {position.sector}
                          </span>
                        </td>
                      </motion.tr>
                    );
                  })}
                </AnimatePresence>
              </tbody>
            </table>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default PieAllocationBreakdown;