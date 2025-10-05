import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useAppContext } from '../contexts/AppContext';
import { apiService } from '../services/api';
import MetricCard from '../components/MetricCard';
import AnimatedMetricCard from '../components/AnimatedMetricCard';
import DashboardGrid from '../components/DashboardGrid';
import LoadingSkeleton from '../components/LoadingSkeleton';
import ResponsiveContainer from '../components/ResponsiveContainer';
import PieChart from '../components/PieChart';
import PieList from '../components/PieList';
import ConnectionStatus from '../components/ConnectionStatus';

import { Icon } from '../components/icons';
import { Pie, Portfolio } from '../types';

const Dashboard: React.FC = () => {
  const { auth } = useAppContext();
  const queryClient = useQueryClient();

  // Fetch data when user is authenticated and has Trading 212 connection
  const { data: portfolioData, isLoading: portfolioLoading, error: portfolioError } = useQuery({
    queryKey: ['portfolio'],
    queryFn: apiService.getPortfolio,
    enabled: auth.isAuthenticated && auth.hasTrading212Connection,
    retry: 3, // Exactly 3 retries
    refetchInterval: false, // Disable automatic refetching
    refetchOnWindowFocus: false,
  });

  // Fetch pies data
  const { data: piesData, isLoading: piesLoading, error: piesError } = useQuery({
    queryKey: ['pies'],
    queryFn: apiService.getPies,
    enabled: auth.isAuthenticated && auth.hasTrading212Connection,
    retry: 3, // Exactly 3 retries
    refetchInterval: false, // Disable automatic refetching
    refetchOnWindowFocus: false,
  });

  const portfolio: Portfolio | undefined = portfolioData;
  const pies: Pie[] = piesData || [];

  // Debug logging (only in development)
  if (process.env.NODE_ENV === 'development') {
    console.log('Dashboard render:', {
      isAuthenticated: auth.isAuthenticated,
      hasTrading212Connection: auth.hasTrading212Connection,
      portfolioData,
      piesData,
      portfolioLoading,
      piesLoading,
      portfolioError,
      piesError
    });
  }

  // Show loading state while data is being fetched (only if queries are enabled)
  const shouldShowLoading = (portfolioLoading || piesLoading) && (auth.isAuthenticated && auth.hasTrading212Connection);
  if (shouldShowLoading) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton variant="dashboard" columns={4} />
      </div>
    );
  }

  // Show sample data if not authenticated or no Trading 212 connection
  if (!auth.isAuthenticated || !auth.hasTrading212Connection) {
    // Sample portfolio data for preview
    const samplePortfolio = {
      totalValue: 125430.50,
      totalInvested: 100000.00,
      totalReturn: 25430.50,
      returnPercentage: 25.43,
      lastUpdated: new Date().toISOString(),
    };

    const samplePies = [
      {
        id: 'tech-growth',
        name: 'Tech Growth',
        totalValue: 45230.20,
        investedAmount: 37000.00,
        returnPct: 22.3,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: 'dividend-stocks',
        name: 'Dividend Stocks',
        totalValue: 32150.75,
        investedAmount: 28000.00,
        returnPct: 14.8,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: 'emerging-markets',
        name: 'Emerging Markets',
        totalValue: 28049.30,
        investedAmount: 21000.00,
        returnPct: 33.6,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
      {
        id: 'bonds-stable',
        name: 'Bonds & Stable',
        totalValue: 20000.25,
        investedAmount: 14000.00,
        returnPct: 42.9,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      },
    ];

    return (
      <div className="space-y-6">
        {/* Header with connection notice */}
        <ResponsiveContainer 
          variant="section" 
          gradient={true} 
          className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-700"
          animationStyle="from-top"
        >
          <div className="flex items-center">
            <div className="text-blue-400 mr-3">
              <Icon name="Info" size="xl" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-blue-900 dark:text-blue-100 mb-2">
                Portfolio Overview
              </h2>
              <p className="text-blue-700 dark:text-blue-300 mb-4">
                Welcome to your Trading 212 Portfolio Dashboard. Connect your API to view your real portfolio data.
                {!auth.isAuthenticated
                  ? ' Create a session and connect your Trading 212 API to view real data.'
                  : ' Connect your Trading 212 API to view your actual portfolio data.'
                }
              </p>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <ConnectionStatus />
                  <span className="text-sm text-blue-600 dark:text-blue-400">
                    {!auth.isAuthenticated
                      ? 'Session and API connection required for real data'
                      : 'Trading 212 API connection required for real data'
                    }
                  </span>
                </div>
                <Link
                  to="/settings"
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 hover:scale-105"
                >
                  {!auth.isAuthenticated ? 'Setup Connection' : 'Connect Trading 212'}
                </Link>
              </div>
            </div>
          </div>
        </ResponsiveContainer>

        {/* Key Metrics with sample data */}
        <ResponsiveContainer 
          variant="card" 
          animationStyle="from-bottom" 
          animationDelay={0.1}
          hoverEffect={true}
        >
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Portfolio Overview
          </h3>
          <DashboardGrid columns={4} staggerDelay={0.15} animationStyle="from-bottom">
          <AnimatedMetricCard
            title="Total Value"
            value={samplePortfolio.totalValue}
            loading={false}
            trend={{
              value: samplePortfolio.totalReturn,
              isPositive: samplePortfolio.totalReturn >= 0,
              prefix: '£'
            }}
            icon={<Icon name="DollarSign" size="lg" />}
            gradient={true}
            animationDelay={0}
          />
          <AnimatedMetricCard
            title="Total Return"
            value={`${samplePortfolio.returnPercentage.toFixed(2)}%`}
            loading={false}
            trend={{
              value: samplePortfolio.totalReturn,
              isPositive: samplePortfolio.totalReturn >= 0,
              prefix: '£'
            }}
            subtitle={`${samplePortfolio.totalReturn >= 0 ? '+' : ''}£${samplePortfolio.totalReturn.toLocaleString()}`}
            icon={<Icon name="TrendingUp" size="lg" />}
            gradient={true}
            animationDelay={0.1}
          />
          <AnimatedMetricCard
            title="Total Invested"
            value={samplePortfolio.totalInvested}
            loading={false}
            subtitle="Capital deployed"
            icon={<Icon name="Calculator" size="lg" />}
            gradient={true}
            animationDelay={0.2}
          />
          <AnimatedMetricCard
            title="Active Pies"
            value={samplePies.length}
            loading={false}
            subtitle={`${samplePies.filter(pie => pie.totalValue > 0).length} with positions`}
            icon={<Icon name="PieChart" size="lg" />}
            gradient={true}
            animationDelay={0.3}
          />
          </DashboardGrid>
        </ResponsiveContainer>

        {/* Performance Summary */}
        <ResponsiveContainer 
          variant="card" 
          animationStyle="from-left" 
          animationDelay={0.4}
          hoverEffect={true}
        >
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Performance Summary
          </h3>
          <DashboardGrid columns={3} staggerDelay={0.1}>
            <ResponsiveContainer 
              variant="card" 
              padding="lg" 
              className="text-center"
              gradient={true}
              hoverEffect={true}
            >
              <div className="text-2xl font-bold text-gray-900">
                {samplePortfolio.returnPercentage.toFixed(2)}%
              </div>
              <div className="text-sm text-gray-600 mt-1">Total Return</div>
              <div className={`text-xs mt-1 ${samplePortfolio.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {samplePortfolio.totalReturn >= 0 ? '+' : ''}£{samplePortfolio.totalReturn.toLocaleString()}
              </div>
            </ResponsiveContainer>
            <ResponsiveContainer 
              variant="card" 
              padding="lg" 
              className="text-center"
              gradient={true}
              hoverEffect={true}
            >
              <div className="text-2xl font-bold text-gray-900">
                {samplePies.filter(pie => pie.totalValue > 0).length}
              </div>
              <div className="text-sm text-gray-600 mt-1">Active Strategies</div>
              <div className="text-xs text-gray-500 mt-1">
                {samplePies.length} total pies
              </div>
            </ResponsiveContainer>
            <ResponsiveContainer 
              variant="card" 
              padding="lg" 
              className="text-center"
              gradient={true}
              hoverEffect={true}
            >
              <div className="text-2xl font-bold text-gray-900">
                {((samplePortfolio.totalValue / samplePortfolio.totalInvested - 1) * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600 mt-1">Portfolio Growth</div>
              <div className="text-xs text-gray-500 mt-1">
                Since inception
              </div>
            </ResponsiveContainer>
          </DashboardGrid>
        </ResponsiveContainer>

        {/* Portfolio Allocation and Pies */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Portfolio Allocation Chart */}
          <ResponsiveContainer 
            variant="card" 
            animationStyle="from-left" 
            animationDelay={0.5}
            hoverEffect={true}
          >
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Portfolio Allocation
            </h3>
            <PieChart
              data={samplePies.map(pie => ({
                name: pie.name,
                value: pie.totalValue,
                percentage: (pie.totalValue / samplePortfolio.totalValue) * 100
              }))}
              loading={false}
            />
          </ResponsiveContainer>

          {/* Pie Performance List */}
          <ResponsiveContainer 
            variant="card" 
            animationStyle="from-right" 
            animationDelay={0.6}
            hoverEffect={true}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Pie Performance
              </h3>
              <Link
                to="/pie-analysis"
                className="text-blue-600 hover:text-blue-800  text-sm font-medium transition-colors duration-200 hover:scale-105"
              >
                View Details →
              </Link>
            </div>
            <PieList
              pies={samplePies}
              loading={false}
              maxItems={5}
            />
          </ResponsiveContainer>
        </div>


      </div>
    );
  }

  // Show error state
  if (portfolioError || piesError) {
    const portfolioErr = portfolioError as any;
    const piesErr = piesError as any;
    const errorMessage = portfolioErr?.message || piesErr?.message || 'An unexpected error occurred';
    const errorStatus = portfolioErr?.status || piesErr?.status;
    const isConnectionError = errorMessage.toLowerCase().includes('network') || errorMessage.toLowerCase().includes('connection');
    const isAuthError = errorStatus === 401 || errorStatus === 403;

    return (
      <div className="space-y-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <div className="text-red-400 mr-3">
              <Icon name="AlertTriangle" size="xl" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-medium text-red-800">
                {isAuthError ? 'Authentication Error' :
                  isConnectionError ? 'Connection Error' :
                    'Failed to load portfolio data'}
              </h3>
              <p className="text-red-700 mt-1">
                {errorMessage}
              </p>
              {errorStatus && (
                <p className="text-red-600 mt-1 text-sm">
                  Error Code: {errorStatus}
                </p>
              )}
              {isConnectionError && (
                <p className="text-red-600 mt-2 text-sm">
                  Please check your internet connection and Trading 212 API status.
                </p>
              )}
              {isAuthError && (
                <p className="text-red-600 mt-2 text-sm">
                  Your session may have expired. Please reconnect your Trading 212 API.
                </p>
              )}
              <div className="mt-4 flex flex-wrap gap-3">
                <button
                  onClick={() => {
                    // Clear React Query cache and retry
                    queryClient.invalidateQueries({ queryKey: ['portfolio'] });
                    queryClient.invalidateQueries({ queryKey: ['pies'] });
                  }}
                  className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 text-sm font-medium"
                >
                  Retry Now
                </button>
                <Link
                  to="/settings"
                  className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 text-sm font-medium"
                >
                  Check API Setup
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Show placeholder cards even in error state */}
        <DashboardGrid columns={4} staggerDelay={0.1} animationStyle="from-bottom">
          <AnimatedMetricCard
            title="Total Value"
            value="--"
            subtitle="Data unavailable"
            loading={false}
            icon={<Icon name="DollarSign" size="lg" />}
            animationDelay={0}
          />
          <AnimatedMetricCard
            title="Total Return"
            value="--"
            subtitle="Data unavailable"
            loading={false}
            icon={<Icon name="TrendingUp" size="lg" />}
            animationDelay={0.1}
          />
          <AnimatedMetricCard
            title="Total Invested"
            value="--"
            subtitle="Data unavailable"
            loading={false}
            icon={<Icon name="Calculator" size="lg" />}
            animationDelay={0.2}
          />
          <AnimatedMetricCard
            title="Active Pies"
            value="--"
            subtitle="Data unavailable"
            loading={false}
            icon={<Icon name="PieChart" size="lg" />}
            animationDelay={0.3}
          />
        </DashboardGrid>
      </div>
    );
  }

  // Show empty state if no data is available
  if (!portfolio && !portfolioLoading && !pies.length && !piesLoading) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Portfolio Overview
          </h2>
          <div className="text-center py-12">
            <div className="text-gray-500 mb-4">
              <Icon name="BarChart" size="2xl" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Load Your Portfolio</h3>
            <p className="text-gray-500 mb-6">
              Your Trading 212 connection is set up. Click "Fetch Data" below to load your portfolio information.
            </p>

            <div className="flex justify-center space-x-3">
              <Link
                to="/settings"
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Manage API Connection
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <ResponsiveContainer 
        variant="section" 
        animationStyle="from-top" 
        gradient={true}
      >
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Portfolio Overview
            </h2>
            <p className="text-gray-600">
              Your Trading 212 portfolio performance and allocation
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <ConnectionStatus />
            {portfolio?.lastUpdated && (
              <span className="text-sm text-gray-600">
                Updated: {new Date(portfolio.lastUpdated).toLocaleString()}
              </span>
            )}
          </div>
        </div>
      </ResponsiveContainer>

      {/* Key Metrics - Only show if we have portfolio data */}
      {portfolio && (
        <ResponsiveContainer 
          variant="card" 
          animationStyle="from-bottom" 
          animationDelay={0.1}
          hoverEffect={true}
        >
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Portfolio Overview
          </h3>
          <DashboardGrid columns={4} staggerDelay={0.15} animationStyle="from-bottom">
          <AnimatedMetricCard
            title="Total Value"
            value={portfolio.totalValue || 0}
            loading={portfolioLoading}
            trend={portfolio.totalReturn ? {
              value: portfolio.totalReturn,
              isPositive: portfolio.totalReturn >= 0,
              prefix: '£'
            } : undefined}
            icon={<Icon name="DollarSign" size="lg" />}
            gradient={true}
            animationDelay={0}
          />
          <AnimatedMetricCard
            title="Total Return"
            value={portfolio.returnPercentage ? `${portfolio.returnPercentage.toFixed(2)}%` : '--'}
            loading={portfolioLoading}
            trend={portfolio.totalReturn ? {
              value: portfolio.totalReturn,
              isPositive: portfolio.totalReturn >= 0,
              prefix: '£'
            } : undefined}
            subtitle={portfolio.totalReturn ? `${portfolio.totalReturn >= 0 ? '+' : ''}£${portfolio.totalReturn.toLocaleString()}` : undefined}
            icon={<Icon name="TrendingUp" size="lg" />}
            gradient={true}
            animationDelay={0.1}
          />
          <AnimatedMetricCard
            title="Total Invested"
            value={portfolio.totalInvested || 0}
            loading={portfolioLoading}
            subtitle="Capital deployed"
            icon={<Icon name="Calculator" size="lg" />}
            gradient={true}
            animationDelay={0.2}
          />
          <AnimatedMetricCard
            title="Active Pies"
            value={pies.length}
            loading={piesLoading}
            subtitle={`${pies.filter(pie => pie.totalValue > 0).length} with positions`}
            icon={<Icon name="PieChart" size="lg" />}
            gradient={true}
            animationDelay={0.3}
          />
          </DashboardGrid>
        </ResponsiveContainer>
      )}

      {/* Performance Summary */}
      {portfolio && (
        <ResponsiveContainer 
          variant="card" 
          animationStyle="from-left" 
          animationDelay={0.4}
          hoverEffect={true}
        >
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Performance Summary
          </h3>
          <DashboardGrid columns={3} staggerDelay={0.1}>
            <ResponsiveContainer 
              variant="card" 
              padding="lg" 
              className="text-center"
              gradient={true}
              hoverEffect={true}
            >
              <div className="text-2xl font-bold text-gray-900">
                {portfolio.returnPercentage ? `${portfolio.returnPercentage.toFixed(2)}%` : '--'}
              </div>
              <div className="text-sm text-gray-600 mt-1">Total Return</div>
              <div className={`text-xs mt-1 ${portfolio.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {portfolio.totalReturn >= 0 ? '+' : ''}£{portfolio.totalReturn?.toLocaleString() || '--'}
              </div>
            </ResponsiveContainer>
            <ResponsiveContainer 
              variant="card" 
              padding="lg" 
              className="text-center"
              gradient={true}
              hoverEffect={true}
            >
              <div className="text-2xl font-bold text-gray-900">
                {pies.filter(pie => pie.totalValue > 0).length}
              </div>
              <div className="text-sm text-gray-600 mt-1">Active Strategies</div>
              <div className="text-xs text-gray-500 mt-1">
                {pies.length} total pies
              </div>
            </ResponsiveContainer>
            <ResponsiveContainer 
              variant="card" 
              padding="lg" 
              className="text-center"
              gradient={true}
              hoverEffect={true}
            >
              <div className="text-2xl font-bold text-gray-900">
                {portfolio.totalValue && portfolio.totalInvested
                  ? `${((portfolio.totalValue / portfolio.totalInvested - 1) * 100).toFixed(1)}%`
                  : '--'
                }
              </div>
              <div className="text-sm text-gray-600 mt-1">Portfolio Growth</div>
              <div className="text-xs text-gray-500 mt-1">
                Since inception
              </div>
            </ResponsiveContainer>
          </DashboardGrid>
        </ResponsiveContainer>
      )}

      {/* Portfolio Allocation and Pies - Only show if we have data */}
      {portfolio && pies.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Portfolio Allocation Chart */}
          <ResponsiveContainer 
            variant="card" 
            animationStyle="from-left" 
            animationDelay={0.5}
            hoverEffect={true}
          >
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Portfolio Allocation
            </h3>
            <PieChart
              data={pies.map(pie => ({
                name: pie.name,
                value: pie.totalValue,
                percentage: portfolio.totalValue ? (pie.totalValue / portfolio.totalValue) * 100 : 0
              }))}
              loading={piesLoading}
            />
          </ResponsiveContainer>

          {/* Pie Performance List */}
          <ResponsiveContainer 
            variant="card" 
            animationStyle="from-right" 
            animationDelay={0.6}
            hoverEffect={true}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Pie Performance
              </h3>
              <Link
                to="/pie-analysis"
                className="text-blue-600 hover:text-blue-800  text-sm font-medium transition-colors duration-200 hover:scale-105"
              >
                View Details →
              </Link>
            </div>
            <PieList
              pies={pies}
              loading={piesLoading}
              maxItems={5}
            />
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default Dashboard;