import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useAppContext } from '../contexts/AppContext';
import { apiService } from '../services/api';
import MetricCard from '../components/MetricCard';
import PieChart from '../components/PieChart';
import PieList from '../components/PieList';
import ConnectionStatus from '../components/ConnectionStatus';
import AuthTest from '../components/AuthTest';
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
        <div className="bg-white rounded-lg shadow p-6">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[...Array(4)].map((_, index) => (
            <MetricCard
              key={index}
              title="Loading..."
              value="--"
              loading={true}
            />
          ))}
        </div>
      </div>
    );
  }

  // Show sample data if not authenticated or no Trading 212 connection
  if (!auth.isAuthenticated || !auth.hasTrading212Connection) {
    // Sample portfolio data for demo purposes
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
        {/* Header with demo notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center">
            <div className="text-blue-400 mr-3">
              <Icon name="Info" size="xl" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-blue-900 mb-2">
                Portfolio Overview (Demo Mode)
              </h2>
              <p className="text-blue-700 mb-4">
                Welcome to your Trading 212 Portfolio Dashboard. This is showing sample data for demonstration purposes.
                {!auth.isAuthenticated
                  ? ' Create a session and connect your Trading 212 API to view real data.'
                  : ' Connect your Trading 212 API to view your actual portfolio data.'
                }
              </p>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <ConnectionStatus />
                  <span className="text-sm text-blue-600">
                    {!auth.isAuthenticated
                      ? 'Session and API connection required for real data'
                      : 'Trading 212 API connection required for real data'
                    }
                  </span>
                </div>
                <Link
                  to="/api-setup"
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  {!auth.isAuthenticated ? 'Setup Connection' : 'Connect Trading 212'}
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Key Metrics with sample data */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <MetricCard
            title="Total Value"
            value={`£${samplePortfolio.totalValue.toLocaleString()}`}
            loading={false}
            trend={{
              value: samplePortfolio.totalReturn,
              isPositive: samplePortfolio.totalReturn >= 0,
              prefix: '£'
            }}
            icon={<Icon name="DollarSign" size="lg" />}
          />
          <MetricCard
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
          />
          <MetricCard
            title="Total Invested"
            value={`£${samplePortfolio.totalInvested.toLocaleString()}`}
            loading={false}
            subtitle="Capital deployed"
            icon={<Icon name="Calculator" size="lg" />}
          />
          <MetricCard
            title="Active Pies"
            value={samplePies.length.toString()}
            loading={false}
            subtitle={`${samplePies.filter(pie => pie.totalValue > 0).length} with positions`}
            icon={<Icon name="PieChart" size="lg" />}
          />
        </div>

        {/* Performance Summary */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Performance Summary
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">
                {samplePortfolio.returnPercentage.toFixed(2)}%
              </div>
              <div className="text-sm text-gray-500 mt-1">Total Return</div>
              <div className={`text-xs mt-1 ${samplePortfolio.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {samplePortfolio.totalReturn >= 0 ? '+' : ''}£{samplePortfolio.totalReturn.toLocaleString()}
              </div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">
                {samplePies.filter(pie => pie.totalValue > 0).length}
              </div>
              <div className="text-sm text-gray-500 mt-1">Active Strategies</div>
              <div className="text-xs text-gray-400 mt-1">
                {samplePies.length} total pies
              </div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">
                {((samplePortfolio.totalValue / samplePortfolio.totalInvested - 1) * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-500 mt-1">Portfolio Growth</div>
              <div className="text-xs text-gray-400 mt-1">
                Since inception
              </div>
            </div>
          </div>
        </div>

        {/* Portfolio Allocation and Pies */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Portfolio Allocation Chart */}
          <div className="bg-white rounded-lg shadow p-6">
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
          </div>

          {/* Pie Performance List */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Pie Performance
              </h3>
              <Link
                to="/pie-analysis"
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                View Details →
              </Link>
            </div>
            <PieList
              pies={samplePies}
              loading={false}
              maxItems={5}
            />
          </div>
        </div>

        {/* Debug information in development */}
        {process.env.NODE_ENV === 'development' && (
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-2">Development Info</h4>
            <AuthTest />
          </div>
        )}
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
                  to="/api-setup"
                  className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 text-sm font-medium"
                >
                  Check API Setup
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Show placeholder cards even in error state */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <MetricCard
            title="Total Value"
            value="--"
            subtitle="Data unavailable"
            loading={false}
            icon={<Icon name="DollarSign" size="lg" />}
          />
          <MetricCard
            title="Total Return"
            value="--"
            subtitle="Data unavailable"
            loading={false}
            icon={<Icon name="TrendingUp" size="lg" />}
          />
          <MetricCard
            title="Total Invested"
            value="--"
            subtitle="Data unavailable"
            loading={false}
            icon={<Icon name="Calculator" size="lg" />}
          />
          <MetricCard
            title="Active Pies"
            value="--"
            subtitle="Data unavailable"
            loading={false}
            icon={<Icon name="PieChart" size="lg" />}
          />
        </div>
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
            <div className="text-gray-400 mb-4">
              <Icon name="BarChart" size="2xl" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Load Your Portfolio</h3>
            <p className="text-gray-500 mb-6">
              Your Trading 212 connection is set up. Click "Fetch Data" below to load your portfolio information.
            </p>
            {process.env.NODE_ENV === 'development' && (
              <div className="mb-6">
                <AuthTest />
              </div>
            )}
            <div className="flex justify-center space-x-3">
              <Link
                to="/api-setup"
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
      <div className="bg-white rounded-lg shadow p-6">
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
              <span className="text-sm text-gray-500">
                Updated: {new Date(portfolio.lastUpdated).toLocaleString()}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Key Metrics - Only show if we have portfolio data */}
      {portfolio && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <MetricCard
            title="Total Value"
            value={portfolio.totalValue ? `£${portfolio.totalValue.toLocaleString()}` : '--'}
            loading={portfolioLoading}
            trend={portfolio.totalReturn ? {
              value: portfolio.totalReturn,
              isPositive: portfolio.totalReturn >= 0,
              prefix: '£'
            } : undefined}
            icon={<Icon name="DollarSign" size="lg" />}
          />
          <MetricCard
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
          />
          <MetricCard
            title="Total Invested"
            value={portfolio.totalInvested ? `£${portfolio.totalInvested.toLocaleString()}` : '--'}
            loading={portfolioLoading}
            subtitle="Capital deployed"
            icon={<Icon name="Calculator" size="lg" />}
          />
          <MetricCard
            title="Active Pies"
            value={pies.length.toString()}
            loading={piesLoading}
            subtitle={`${pies.filter(pie => pie.totalValue > 0).length} with positions`}
            icon={<Icon name="PieChart" size="lg" />}
          />
        </div>
      )}

      {/* Performance Summary */}
      {portfolio && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Performance Summary
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">
                {portfolio.returnPercentage ? `${portfolio.returnPercentage.toFixed(2)}%` : '--'}
              </div>
              <div className="text-sm text-gray-500 mt-1">Total Return</div>
              <div className={`text-xs mt-1 ${portfolio.totalReturn >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {portfolio.totalReturn >= 0 ? '+' : ''}£{portfolio.totalReturn?.toLocaleString() || '--'}
              </div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">
                {pies.filter(pie => pie.totalValue > 0).length}
              </div>
              <div className="text-sm text-gray-500 mt-1">Active Strategies</div>
              <div className="text-xs text-gray-400 mt-1">
                {pies.length} total pies
              </div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">
                {portfolio.totalValue && portfolio.totalInvested
                  ? `${((portfolio.totalValue / portfolio.totalInvested - 1) * 100).toFixed(1)}%`
                  : '--'
                }
              </div>
              <div className="text-sm text-gray-500 mt-1">Portfolio Growth</div>
              <div className="text-xs text-gray-400 mt-1">
                Since inception
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Portfolio Allocation and Pies - Only show if we have data */}
      {portfolio && pies.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Portfolio Allocation Chart */}
          <div className="bg-white rounded-lg shadow p-6">
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
          </div>

          {/* Pie Performance List */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Pie Performance
              </h3>
              <Link
                to="/pie-analysis"
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                View Details →
              </Link>
            </div>
            <PieList
              pies={pies}
              loading={piesLoading}
              maxItems={5}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;