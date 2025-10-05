import React from 'react';
import { motion } from 'framer-motion';
import { Icon } from './icons';
import {
  motionConfigs,
  createCardStyles,
  cn,
  staggerConfigs,
  gradientStyles,
  glassStyles,
} from '../utils';

// Sample portfolio data
const portfolioData = {
  totalValue: 125430.50,
  totalInvested: 100000.00,
  totalReturn: 25430.50,
  returnPercentage: 25.43,
  todayChange: -1234.56,
  todayChangePercentage: -0.98,
  dividendYield: 3.2,
  monthlyDividends: 267.50,
};

const pieData = [
  {
    id: 'tech-growth',
    name: 'Tech Growth',
    value: 45230.20,
    percentage: 36.1,
    return: 8234.50,
    returnPercentage: 22.3,
    color: 'from-blue-500 to-purple-600',
  },
  {
    id: 'dividend-stocks',
    name: 'Dividend Stocks',
    value: 32150.75,
    percentage: 25.6,
    return: 4150.75,
    returnPercentage: 14.8,
    color: 'from-green-500 to-emerald-600',
  },
  {
    id: 'emerging-markets',
    name: 'Emerging Markets',
    value: 28049.30,
    percentage: 22.4,
    return: 7049.30,
    returnPercentage: 33.6,
    color: 'from-orange-500 to-red-600',
  },
  {
    id: 'bonds-stable',
    name: 'Bonds & Stable',
    value: 20000.25,
    percentage: 15.9,
    return: 6000.25,
    returnPercentage: 42.9,
    color: 'from-indigo-500 to-blue-600',
  },
];

const topHoldings = [
  { symbol: 'AAPL', name: 'Apple Inc.', value: 12450.30, percentage: 9.9, change: 2.3 },
  { symbol: 'MSFT', name: 'Microsoft Corp.', value: 10230.50, percentage: 8.2, change: -1.2 },
  { symbol: 'GOOGL', name: 'Alphabet Inc.', value: 8750.20, percentage: 7.0, change: 3.1 },
  { symbol: 'TSLA', name: 'Tesla Inc.', value: 7890.40, percentage: 6.3, change: -4.5 },
  { symbol: 'NVDA', name: 'NVIDIA Corp.', value: 6540.80, percentage: 5.2, change: 5.7 },
];

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
};

const formatPercentage = (value: number) => {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
};

const MetricCard: React.FC<{
  title: string;
  value: string;
  change?: string;
  positive?: boolean;
  delay?: number;
}> = ({ title, value, change, positive, delay = 0 }) => (
  <motion.div
    className={cn(createCardStyles('glass'), 'relative overflow-hidden')}
    {...motionConfigs.metric}
    transition={{ delay }}
    whileHover={{ scale: 1.02, y: -2 }}
    whileTap={{ scale: 0.98 }}
  >
    {/* Background gradient */}
    <div className={cn(
      'absolute inset-0 opacity-10',
      positive !== undefined 
        ? positive 
          ? gradientStyles.success 
          : gradientStyles.danger
        : gradientStyles.primary
    )} />
    
    <div className="relative z-10">
      <h3 className="text-sm font-medium text-gray-300 mb-2">
        {title}
      </h3>
      <p className="text-2xl font-bold text-white mb-1">
        {value}
      </p>
      {change && (
        <p className={cn(
          'text-sm font-medium',
          positive ? 'text-green-400' : 'text-red-400'
        )}>
          {change}
        </p>
      )}
    </div>
  </motion.div>
);

const PieCard: React.FC<{
  pie: typeof pieData[0];
  delay?: number;
}> = ({ pie, delay = 0 }) => (
  <motion.div
    className={cn(createCardStyles('glass'), 'relative overflow-hidden')}
    {...motionConfigs.card}
    transition={{ delay }}
    whileHover={{ scale: 1.02, y: -2 }}
    whileTap={{ scale: 0.98 }}
  >
    {/* Background gradient */}
    <div className={cn(
      'absolute inset-0 opacity-20 bg-gradient-to-br',
      pie.color
    )} />
    
    <div className="relative z-10">
      <div className="flex justify-between items-start mb-3">
        <h3 className="font-semibold text-white">{pie.name}</h3>
        <span className="text-sm text-gray-300">{pie.percentage}%</span>
      </div>
      
      <div className="space-y-2">
        <div>
          <p className="text-xl font-bold text-white">
            {formatCurrency(pie.value)}
          </p>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-300">Return:</span>
          <span className={cn(
            'text-sm font-medium',
            pie.returnPercentage >= 0 ? 'text-green-400' : 'text-red-400'
          )}>
            {formatCurrency(pie.return)} ({formatPercentage(pie.returnPercentage)})
          </span>
        </div>
      </div>
    </div>
  </motion.div>
);

const HoldingRow: React.FC<{
  holding: typeof topHoldings[0];
  delay?: number;
}> = ({ holding, delay = 0 }) => (
  <motion.div
    className={cn(
      glassStyles.light,
      'p-4 rounded-lg hover:bg-white/20 transition-all duration-200'
    )}
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay, duration: 0.3 }}
    whileHover={{ scale: 1.01, x: 4 }}
  >
    <div className="flex justify-between items-center">
      <div>
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-purple-600 rounded-full flex items-center justify-center">
            <Icon name="TrendingUp" size="sm" className="text-white" />
          </div>
          <div>
            <h4 className="font-medium text-white">{holding.symbol}</h4>
            <p className="text-sm text-gray-300">{holding.name}</p>
          </div>
        </div>
      </div>
      
      <div className="text-right">
        <p className="font-semibold text-white">
          {formatCurrency(holding.value)}
        </p>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-300">{holding.percentage}%</span>
          <span className={cn(
            'text-sm font-medium',
            holding.change >= 0 ? 'text-green-400' : 'text-red-400'
          )}>
            {formatPercentage(holding.change)}
          </span>
        </div>
      </div>
    </div>
  </motion.div>
);

const PortfolioOverview: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          className="text-center"
          {...motionConfigs.card}
        >
          <h1 className="text-4xl font-bold text-white mb-2">
            Portfolio Dashboard
          </h1>
          <p className="text-gray-300 text-lg">
            Real-time portfolio analytics and insights
          </p>
        </motion.div>

        {/* Portfolio Metrics */}
        <motion.div
          variants={staggerConfigs.container}
          initial="initial"
          animate="animate"
        >
          <motion.h2
            className="text-2xl font-bold text-white mb-6"
            variants={{
              initial: { opacity: 0, y: 20 },
              animate: { opacity: 1, y: 0 },
            }}
          >
            Portfolio Overview
          </motion.h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total Value"
              value={formatCurrency(portfolioData.totalValue)}
              delay={0.1}
            />
            <MetricCard
              title="Total Return"
              value={formatCurrency(portfolioData.totalReturn)}
              change={formatPercentage(portfolioData.returnPercentage)}
              positive={portfolioData.totalReturn >= 0}
              delay={0.2}
            />
            <MetricCard
              title="Today's Change"
              value={formatCurrency(portfolioData.todayChange)}
              change={formatPercentage(portfolioData.todayChangePercentage)}
              positive={portfolioData.todayChange >= 0}
              delay={0.3}
            />
            <MetricCard
              title="Dividend Yield"
              value={`${portfolioData.dividendYield}%`}
              change={formatCurrency(portfolioData.monthlyDividends) + '/mo'}
              positive={true}
              delay={0.4}
            />
          </div>
        </motion.div>

        {/* Pie Breakdown */}
        <motion.div
          variants={staggerConfigs.container}
          initial="initial"
          animate="animate"
        >
          <motion.h2
            className="text-2xl font-bold text-white mb-6"
            variants={{
              initial: { opacity: 0, y: 20 },
              animate: { opacity: 1, y: 0 },
            }}
          >
            Investment Pies
          </motion.h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {pieData.map((pie, index) => (
              <PieCard
                key={pie.id}
                pie={pie}
                delay={0.1 + index * 0.1}
              />
            ))}
          </div>
        </motion.div>

        {/* Top Holdings */}
        <motion.div
          className={cn(createCardStyles('glass'))}
          {...motionConfigs.card}
          transition={{ delay: 0.6 }}
        >
          <h2 className="text-2xl font-bold text-white mb-6">
            Top Holdings
          </h2>
          
          <div className="space-y-3">
            {topHoldings.map((holding, index) => (
              <HoldingRow
                key={holding.symbol}
                holding={holding}
                delay={0.7 + index * 0.1}
              />
            ))}
          </div>
        </motion.div>

        {/* Performance Chart Placeholder */}
        <motion.div
          className={cn(createCardStyles('glass'), 'h-64')}
          {...motionConfigs.chart}
          transition={{ delay: 1.2 }}
        >
          <h2 className="text-2xl font-bold text-white mb-6">
            Performance Chart
          </h2>
          
          <div className="flex items-center justify-center h-40">
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <Icon name="BarChart" size="xl" className="text-white" />
              </div>
              <p className="text-gray-300">
                Interactive charts will be implemented in the next phase
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default PortfolioOverview;