import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  InteractivePieChart,
  AnimatedDonutChart,
  AnimatedTopHoldingsTable,
  AllocationDriftIndicators,
  RebalancingSuggestionCards,
  PieChartData,
  DonutChartData,
  HoldingData,
  AllocationData,
  RebalancingSuggestion
} from '../components/charts';
import { Icon } from '../components/icons';
import { staggerConfigs } from '../utils/animations';

// Sample data for demonstration
const samplePieData: PieChartData[] = [
  { name: 'Growth Pie', value: 15000, percentage: 35.7, color: '#3B82F6', sector: 'Technology', change: 2.5 },
  { name: 'Dividend Pie', value: 12000, percentage: 28.6, color: '#10B981', sector: 'Financial', change: 1.2 },
  { name: 'Value Pie', value: 8000, percentage: 19.0, color: '#F59E0B', sector: 'Healthcare', change: -0.8 },
  { name: 'International Pie', value: 7000, percentage: 16.7, color: '#EF4444', sector: 'Consumer', change: 3.1 },
];

const sampleSectorData: DonutChartData[] = [
  { name: 'Technology', value: 18000, percentage: 42.9, color: '#3B82F6', category: 'sector', description: 'Software, hardware, and tech services' },
  { name: 'Healthcare', value: 8500, percentage: 20.2, color: '#10B981', category: 'sector', description: 'Pharmaceuticals and medical devices' },
  { name: 'Financial', value: 7200, percentage: 17.1, color: '#F59E0B', category: 'sector', description: 'Banks and financial services' },
  { name: 'Consumer Discretionary', value: 4800, percentage: 11.4, color: '#EF4444', category: 'sector', description: 'Retail and consumer goods' },
  { name: 'Industrial', value: 3500, percentage: 8.3, color: '#8B5CF6', category: 'sector', description: 'Manufacturing and industrial services' },
];

const sampleHoldingsData: HoldingData[] = [
  {
    symbol: 'AAPL',
    name: 'Apple Inc.',
    value: 8500,
    percentage: 20.2,
    quantity: 50,
    currentPrice: 170.00,
    change: 125.50,
    changePercentage: 1.5,
    sector: 'Technology',
    country: 'United States',
    assetType: 'STOCK'
  },
  {
    symbol: 'MSFT',
    name: 'Microsoft Corporation',
    value: 7200,
    percentage: 17.1,
    quantity: 20,
    currentPrice: 360.00,
    change: -45.20,
    changePercentage: -0.6,
    sector: 'Technology',
    country: 'United States',
    assetType: 'STOCK'
  },
  {
    symbol: 'VWRL',
    name: 'Vanguard FTSE All-World UCITS ETF',
    value: 6800,
    percentage: 16.2,
    quantity: 65,
    currentPrice: 104.50,
    change: 78.30,
    changePercentage: 1.2,
    sector: 'Diversified',
    country: 'Global',
    assetType: 'ETF'
  },
  {
    symbol: 'GOOGL',
    name: 'Alphabet Inc.',
    value: 5400,
    percentage: 12.9,
    quantity: 40,
    currentPrice: 135.00,
    change: -12.75,
    changePercentage: -0.9,
    sector: 'Technology',
    country: 'United States',
    assetType: 'STOCK'
  },
  {
    symbol: 'JNJ',
    name: 'Johnson & Johnson',
    value: 4200,
    percentage: 10.0,
    quantity: 25,
    currentPrice: 168.00,
    change: 34.60,
    changePercentage: 2.1,
    sector: 'Healthcare',
    country: 'United States',
    assetType: 'STOCK'
  },
  {
    symbol: 'BRK.B',
    name: 'Berkshire Hathaway Inc.',
    value: 3800,
    percentage: 9.0,
    quantity: 10,
    currentPrice: 380.00,
    change: -15.20,
    changePercentage: -0.4,
    sector: 'Financial',
    country: 'United States',
    assetType: 'STOCK'
  },
  {
    symbol: 'TSLA',
    name: 'Tesla, Inc.',
    value: 3200,
    percentage: 7.6,
    quantity: 15,
    currentPrice: 213.33,
    change: 67.80,
    changePercentage: 3.3,
    sector: 'Consumer Discretionary',
    country: 'United States',
    assetType: 'STOCK'
  },
  {
    symbol: 'NVDA',
    name: 'NVIDIA Corporation',
    value: 2900,
    percentage: 6.9,
    quantity: 8,
    currentPrice: 362.50,
    change: 145.20,
    changePercentage: 6.7,
    sector: 'Technology',
    country: 'United States',
    assetType: 'STOCK'
  }
];

const sampleAllocationData: AllocationData[] = [
  {
    name: 'Growth Pie',
    currentPercentage: 35.7,
    targetPercentage: 30.0,
    currentValue: 15000,
    targetValue: 12600,
    drift: 2400,
    driftPercentage: 5.7,
    category: 'pie',
    color: '#3B82F6'
  },
  {
    name: 'Technology Sector',
    currentPercentage: 42.9,
    targetPercentage: 35.0,
    currentValue: 18000,
    targetValue: 14700,
    drift: 3300,
    driftPercentage: 7.9,
    category: 'sector',
    color: '#3B82F6'
  },
  {
    name: 'Dividend Pie',
    currentPercentage: 28.6,
    targetPercentage: 35.0,
    currentValue: 12000,
    targetValue: 14700,
    drift: -2700,
    driftPercentage: -6.4,
    category: 'pie',
    color: '#10B981'
  },
  {
    name: 'International Exposure',
    currentPercentage: 16.7,
    targetPercentage: 25.0,
    currentValue: 7000,
    targetValue: 10500,
    drift: -3500,
    driftPercentage: -8.3,
    category: 'geography',
    color: '#EF4444'
  }
];

const sampleSuggestions: RebalancingSuggestion[] = [
  {
    id: '1',
    type: 'rebalance',
    priority: 'high',
    title: 'Reduce Technology Overweight',
    description: 'Technology sector is 7.9% above target allocation, creating concentration risk.',
    currentAllocation: 42.9,
    targetAllocation: 35.0,
    suggestedAmount: 3300,
    impact: {
      driftReduction: 7.9,
      riskImprovement: 2.3,
      costEstimate: 15.50
    },
    assets: [
      { name: 'Apple Inc.', symbol: 'AAPL', action: 'sell', amount: 1500, percentage: 45.5 },
      { name: 'Microsoft Corporation', symbol: 'MSFT', action: 'sell', amount: 1200, percentage: 36.4 },
      { name: 'NVIDIA Corporation', symbol: 'NVDA', action: 'sell', amount: 600, percentage: 18.2 }
    ],
    reasoning: [
      'Technology sector concentration exceeds risk tolerance',
      'Recent tech rally has pushed allocation above targets',
      'Diversification into other sectors would improve risk-adjusted returns'
    ],
    estimatedTime: '15-20 minutes',
    difficulty: 'easy'
  },
  {
    id: '2',
    type: 'buy',
    priority: 'medium',
    title: 'Increase International Exposure',
    description: 'International allocation is 8.3% below target, missing global diversification benefits.',
    currentAllocation: 16.7,
    targetAllocation: 25.0,
    suggestedAmount: 3500,
    impact: {
      driftReduction: 8.3,
      riskImprovement: 1.8,
      costEstimate: 8.75
    },
    assets: [
      { name: 'Vanguard FTSE All-World UCITS ETF', symbol: 'VWRL', action: 'buy', amount: 2000, percentage: 57.1 },
      { name: 'iShares MSCI Emerging Markets IMI UCITS ETF', symbol: 'IEMI', action: 'buy', amount: 1500, percentage: 42.9 }
    ],
    reasoning: [
      'Geographic diversification reduces portfolio risk',
      'International markets offer different growth opportunities',
      'Currency diversification provides additional protection'
    ],
    estimatedTime: '10-15 minutes',
    difficulty: 'easy'
  },
  {
    id: '3',
    type: 'rebalance',
    priority: 'low',
    title: 'Optimize Dividend Pie Allocation',
    description: 'Minor adjustment to dividend-focused holdings for better yield optimization.',
    currentAllocation: 28.6,
    targetAllocation: 35.0,
    suggestedAmount: 2700,
    impact: {
      driftReduction: 6.4,
      riskImprovement: 0.8,
      costEstimate: 12.25
    },
    assets: [
      { name: 'Johnson & Johnson', symbol: 'JNJ', action: 'buy', amount: 1500, percentage: 55.6 },
      { name: 'Coca-Cola Company', symbol: 'KO', action: 'buy', amount: 1200, percentage: 44.4 }
    ],
    reasoning: [
      'Dividend yield optimization opportunity',
      'Stable dividend growth companies available at attractive prices',
      'Improves overall portfolio income generation'
    ],
    estimatedTime: '20-25 minutes',
    difficulty: 'moderate'
  }
];

const AllocationAnalysis: React.FC = () => {
  const [selectedTimeframe, setSelectedTimeframe] = useState('1M');
  const [loading, setLoading] = useState(false);

  const handleSuggestionAccept = (suggestion: RebalancingSuggestion) => {
    console.log('Accepting suggestion:', suggestion.title);
    // Here you would implement the actual rebalancing logic
  };

  const handleSuggestionDismiss = (suggestion: RebalancingSuggestion) => {
    console.log('Dismissing suggestion:', suggestion.title);
    // Here you would implement the dismissal logic
  };

  const handleHoldingClick = (holding: HoldingData) => {
    console.log('Clicked holding:', holding.symbol);
    // Here you would navigate to detailed holding view
  };

  const handleAllocationClick = (allocation: AllocationData) => {
    console.log('Clicked allocation:', allocation.name);
    // Here you would show detailed allocation analysis
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Allocation & Diversification Analysis
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Interactive portfolio allocation visualizations with animated insights
          </p>
          
          {/* Timeframe selector */}
          <div className="flex items-center justify-center space-x-2 mt-4">
            {['1W', '1M', '3M', '6M', '1Y'].map((timeframe) => (
              <button
                key={timeframe}
                onClick={() => setSelectedTimeframe(timeframe)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  selectedTimeframe === timeframe
                    ? 'bg-primary-500 text-white shadow-md'
                    : 'bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                {timeframe}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Main content grid */}
        <motion.div
          variants={staggerConfigs.container}
          initial="initial"
          animate="animate"
          className="grid grid-cols-1 lg:grid-cols-2 gap-8"
        >
          {/* Interactive Pie Chart */}
          <motion.div variants={staggerConfigs.container}>
            <InteractivePieChart
              data={samplePieData}
              title="Portfolio Allocation by Pie"
              loading={loading}
              height={400}
              showLegend={true}
              showTooltip={true}
              animationDelay={0.1}
              onSegmentClick={(data) => console.log('Pie clicked:', data.name)}
            />
          </motion.div>

          {/* Animated Donut Chart */}
          <motion.div variants={staggerConfigs.container}>
            <AnimatedDonutChart
              data={sampleSectorData}
              title="Sector Breakdown"
              centerLabel="Total Portfolio"
              centerValue="£42,000"
              loading={loading}
              height={400}
              showTooltip={true}
              progressiveLoading={true}
              animationDelay={0.2}
              onSegmentClick={(data) => console.log('Sector clicked:', data.name)}
            />
          </motion.div>
        </motion.div>

        {/* Top Holdings Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <AnimatedTopHoldingsTable
            data={sampleHoldingsData}
            title="Top Holdings Analysis"
            maxRows={8}
            loading={loading}
            showSearch={true}
            showFilters={true}
            animationDelay={0.4}
            onRowClick={handleHoldingClick}
          />
        </motion.div>

        {/* Allocation Drift and Rebalancing */}
        <motion.div
          variants={staggerConfigs.container}
          initial="initial"
          animate="animate"
          className="grid grid-cols-1 xl:grid-cols-2 gap-8"
        >
          {/* Allocation Drift Indicators */}
          <motion.div variants={staggerConfigs.container}>
            <AllocationDriftIndicators
              data={sampleAllocationData}
              title="Allocation Drift Analysis"
              loading={loading}
              showTargets={true}
              driftThreshold={5}
              animationDelay={0.5}
              onItemClick={handleAllocationClick}
            />
          </motion.div>

          {/* Rebalancing Suggestions */}
          <motion.div variants={staggerConfigs.container}>
            <RebalancingSuggestionCards
              suggestions={sampleSuggestions}
              title="Rebalancing Suggestions"
              loading={loading}
              maxSuggestions={5}
              showPriorityFilter={true}
              animationDelay={0.6}
              onSuggestionAccept={handleSuggestionAccept}
              onSuggestionDismiss={handleSuggestionDismiss}
            />
          </motion.div>
        </motion.div>

        {/* Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="flex items-center justify-center space-x-4"
        >
          <button
            onClick={() => setLoading(!loading)}
            className="flex items-center space-x-2 px-6 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-all duration-200 shadow-md hover:shadow-lg"
          >
            <Icon name={loading ? 'X' : 'Refresh'} size="sm" />
            <span>{loading ? 'Stop Loading' : 'Toggle Loading State'}</span>
          </button>
          
          <button
            onClick={() => window.location.reload()}
            className="flex items-center space-x-2 px-6 py-3 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-medium transition-all duration-200 shadow-md hover:shadow-lg"
          >
            <Icon name="Refresh" size="sm" />
            <span>Refresh Data</span>
          </button>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="text-center text-gray-500 dark:text-gray-400 text-sm"
        >
          <p>
            Interactive allocation and diversification visualizations with smooth animations
          </p>
          <p className="mt-1">
            Built with React, Framer Motion, and Recharts
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default AllocationAnalysis;