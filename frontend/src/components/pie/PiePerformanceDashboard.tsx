import React from 'react';
import { motion } from 'framer-motion';
import { Pie } from '../../types/api';
import AnimatedMetricCard from '../AnimatedMetricCard';
import { Icon } from '../icons';
import { containerVariants, listItemVariants } from '../../utils/animations';

interface PiePerformanceDashboardProps {
  pie: Pie | null;
  loading?: boolean;
  onPieSelect?: (pie: Pie) => void;
  availablePies?: Pie[];
}

const PiePerformanceDashboard: React.FC<PiePerformanceDashboardProps> = ({
  pie,
  loading = false,
  onPieSelect,
  availablePies = []
}) => {
  if (loading) {
    return (
      <motion.div
        variants={containerVariants}
        initial="initial"
        animate="animate"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {[...Array(6)].map((_, index) => (
          <motion.div key={index} variants={listItemVariants}>
            <AnimatedMetricCard
              title="Loading..."
              value="0"
              loading={true}
              animationDelay={index * 0.1}
            />
          </motion.div>
        ))}
      </motion.div>
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
          Select a Pie to Analyze
        </h3>
        <p className="text-gray-600">
          Choose a pie from the dropdown above to view detailed performance metrics.
        </p>
      </motion.div>
    );
  }

  // Calculate derived metrics
  const returnAmount = pie.returnAmount || ((pie.returnPercentage / 100) * pie.investedAmount);
  const isPositive = returnAmount >= 0;
  const currentValue = pie.totalValue;
  const investedAmount = pie.investedAmount;
  const returnPercentage = pie.returnPercentage;

  // Mock additional metrics (in real implementation, these would come from API)
  const mockMetrics = {
    volatility: 15.2,
    sharpeRatio: 1.34,
    maxDrawdown: -8.5,
    beta: 1.12,
    dividendYield: 2.8,
    monthlyReturn: 1.2,
    yearToDateReturn: 14.5,
    positionsCount: pie.positions?.length || 0
  };

  const metricCards = [
    {
      title: 'Total Value',
      value: `£${currentValue.toLocaleString()}`,
      icon: <Icon name="DollarSign" size="lg" />,
      gradient: true,
      trend: {
        value: Math.abs(returnAmount),
        isPositive,
        prefix: isPositive ? '+£' : '-£'
      }
    },
    {
      title: 'Total Return',
      value: `${returnPercentage.toFixed(2)}%`,
      icon: <Icon name={isPositive ? 'TrendingUp' : 'TrendingDown'} size="lg" />,
      trend: {
        value: Math.abs(returnAmount),
        isPositive,
        prefix: isPositive ? '+£' : '-£'
      }
    },
    {
      title: 'Invested Amount',
      value: `£${investedAmount.toLocaleString()}`,
      icon: <Icon name="Target" size="lg" />,
      subtitle: 'Original investment'
    },
    {
      title: 'Volatility',
      value: `${mockMetrics.volatility}%`,
      icon: <Icon name="Activity" size="lg" />,
      subtitle: 'Risk measure'
    },
    {
      title: 'Sharpe Ratio',
      value: mockMetrics.sharpeRatio.toFixed(2),
      icon: <Icon name="BarChart" size="lg" />,
      subtitle: 'Risk-adjusted return',
      trend: {
        value: mockMetrics.sharpeRatio,
        isPositive: mockMetrics.sharpeRatio > 1
      }
    },
    {
      title: 'Max Drawdown',
      value: `${mockMetrics.maxDrawdown}%`,
      icon: <Icon name="TrendingDown" size="lg" />,
      subtitle: 'Worst decline',
      trend: {
        value: Math.abs(mockMetrics.maxDrawdown),
        isPositive: false,
        suffix: '%'
      }
    },
    {
      title: 'Beta',
      value: mockMetrics.beta.toFixed(2),
      icon: <Icon name="BarChart3" size="lg" />,
      subtitle: 'Market correlation'
    },
    {
      title: 'Dividend Yield',
      value: `${mockMetrics.dividendYield}%`,
      icon: <Icon name="Coins" size="lg" />,
      subtitle: 'Annual dividend yield'
    },
    {
      title: 'Monthly Return',
      value: `${mockMetrics.monthlyReturn}%`,
      icon: <Icon name="Calendar" size="lg" />,
      trend: {
        value: mockMetrics.monthlyReturn,
        isPositive: mockMetrics.monthlyReturn > 0,
        suffix: '%'
      }
    },
    {
      title: 'YTD Return',
      value: `${mockMetrics.yearToDateReturn}%`,
      icon: <Icon name="Growth" size="lg" />,
      trend: {
        value: mockMetrics.yearToDateReturn,
        isPositive: mockMetrics.yearToDateReturn > 0,
        suffix: '%'
      }
    },
    {
      title: 'Positions',
      value: mockMetrics.positionsCount.toString(),
      icon: <Icon name="Database" size="lg" />,
      subtitle: 'Holdings count'
    },
    {
      title: 'Last Updated',
      value: new Date(pie.updatedAt).toLocaleDateString(),
      icon: <Icon name="Clock" size="lg" />,
      subtitle: 'Data freshness'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Pie Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white"
      >
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">{pie.name}</h2>
            <div className="flex items-center space-x-4 text-blue-100">
              <span>Created: {new Date(pie.createdAt).toLocaleDateString()}</span>
              <span>•</span>
              <span>ID: {pie.id}</span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">
              £{currentValue.toLocaleString()}
            </div>
            <div className={`text-lg ${isPositive ? 'text-green-200' : 'text-red-200'}`}>
              {isPositive ? '+' : ''}£{Math.abs(returnAmount).toLocaleString()} 
              ({returnPercentage.toFixed(2)}%)
            </div>
          </div>
        </div>
      </motion.div>

      {/* Performance Metrics Grid */}
      <motion.div
        variants={containerVariants}
        initial="initial"
        animate="animate"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
      >
        {metricCards.map((card, index) => (
          <motion.div key={card.title} variants={listItemVariants}>
            <AnimatedMetricCard
              title={card.title}
              value={card.value}
              subtitle={card.subtitle}
              icon={card.icon}
              trend={card.trend}
              gradient={card.gradient}
              animationDelay={index * 0.05}
              hoverEffect={true}
              className="h-full"
            />
          </motion.div>
        ))}
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-white/80 backdrop-blur-sm rounded-xl p-6 border border-gray-200"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="flex flex-wrap gap-3">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Icon name="LineChart" size="sm" />
            <span>View Timeline</span>
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Icon name="PieChart" size="sm" />
            <span>View Allocation</span>
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Icon name="BarChart3" size="sm" />
            <span>Compare Pies</span>
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            <Icon name="Download" size="sm" />
            <span>Export Data</span>
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
};

export default PiePerformanceDashboard;