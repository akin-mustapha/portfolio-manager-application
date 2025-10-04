import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAppContext } from '../contexts/AppContext';
import { apiService } from '../services/api';
import MetricCard from '../components/MetricCard';
import PieChart from '../components/PieChart';
import PieList from '../components/PieList';
import ConnectionStatus from '../components/ConnectionStatus';
import { Pie, Portfolio } from '../types';

const Dashboard: React.FC = () => {
  const { auth } = useAppContext();

  // Fetch portfolio data
  const { data: portfolioData, isLoading: portfolioLoading, error: portfolioError } = useQuery({
    queryKey: ['portfolio'],
    queryFn: apiService.getPortfolio,
    enabled: auth.isAuthenticated,
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });

  // Fetch pies data
  const { data: piesData, isLoading: piesLoading, error: piesError } = useQuery({
    queryKey: ['pies'],
    queryFn: apiService.getPies,
    enabled: auth.isAuthenticated,
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });

  const portfolio: Portfolio | undefined = portfolioData;
  const pies: Pie[] = piesData || [];

  // Show connection prompt if not authenticated
  if (!auth.isAuthenticated) {
    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Portfolio Overview
          </h2>
          <p className="text-gray-600 mb-6">
            Welcome to your Trading 212 Portfolio Dashboard. 
            Connect your Trading 212 API to get started.
          </p>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <ConnectionStatus />
              <span className="text-sm text-gray-500">
                API connection required to view portfolio data
              </span>
            </div>
            <Link
              to="/api-setup"
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Connect API
            </Link>
          </div>
        </div>
        
        {/* Placeholder cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <MetricCard
            title="Total Value"
            value="--"
            subtitle="Connect API to view data"
            loading={false}
          />
          <MetricCard
            title="Total Return"
            value="--"
            subtitle="Connect API to view data"
            loading={false}
          />
          <MetricCard
            title="Active Pies"
            value="--"
            subtitle="Connect API to view data"
            loading={false}
          />
        </div>
      </div>
    );
  }

  // Show error state
  if (portfolioError || piesError) {
    const errorMessage = (portfolioError as any)?.message || (piesError as any)?.message || 'An unexpected error occurred';
    const isConnectionError = errorMessage.toLowerCase().includes('network') || errorMessage.toLowerCase().includes('connection');
    
    return (
      <div className="space-y-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <div className="text-red-400 mr-3 text-2xl">⚠️</div>
            <div className="flex-1">
              <h3 className="text-lg font-medium text-red-800">
                {isConnectionError ? 'Connection Error' : 'Failed to load portfolio data'}
              </h3>
              <p className="text-red-700 mt-1">
                {errorMessage}
              </p>
              {isConnectionError && (
                <p className="text-red-600 mt-2 text-sm">
                  Please check your internet connection and Trading 212 API status.
                </p>
              )}
              <div className="mt-4 flex flex-wrap gap-3">
                <button
                  onClick={() => window.location.reload()}
                  className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 text-sm font-medium"
                >
                  Retry Loading
                </button>
                <Link
                  to="/api-setup"
                  className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 text-sm font-medium"
                >
                  Check API Setup
                </Link>
                <Link
                  to="/settings"
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm font-medium"
                >
                  Settings
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
            icon="💰"
          />
          <MetricCard
            title="Total Return"
            value="--"
            subtitle="Data unavailable"
            loading={false}
            icon="📈"
          />
          <MetricCard
            title="Total Invested"
            value="--"
            subtitle="Data unavailable"
            loading={false}
            icon="💼"
          />
          <MetricCard
            title="Active Pies"
            value="--"
            subtitle="Data unavailable"
            loading={false}
            icon="🥧"
          />
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

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard
          title="Total Value"
          value={portfolio?.totalValue ? `£${portfolio.totalValue.toLocaleString()}` : '--'}
          loading={portfolioLoading}
          trend={portfolio?.totalReturn ? {
            value: portfolio.totalReturn,
            isPositive: portfolio.totalReturn >= 0,
            prefix: '£'
          } : undefined}
          icon="💰"
        />
        <MetricCard
          title="Total Return"
          value={portfolio?.returnPercentage ? `${portfolio.returnPercentage.toFixed(2)}%` : '--'}
          loading={portfolioLoading}
          trend={portfolio?.totalReturn ? {
            value: portfolio.totalReturn,
            isPositive: portfolio.totalReturn >= 0,
            prefix: '£'
          } : undefined}
          subtitle={portfolio?.totalReturn ? `${portfolio.totalReturn >= 0 ? '+' : ''}£${portfolio.totalReturn.toLocaleString()}` : undefined}
          icon="📈"
        />
        <MetricCard
          title="Total Invested"
          value={portfolio?.totalInvested ? `£${portfolio.totalInvested.toLocaleString()}` : '--'}
          loading={portfolioLoading}
          subtitle="Capital deployed"
          icon="💼"
        />
        <MetricCard
          title="Active Pies"
          value={pies.length.toString()}
          loading={piesLoading}
          subtitle={`${pies.filter(pie => pie.totalValue > 0).length} with positions`}
          icon="🥧"
        />
      </div>

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

      {/* Portfolio Allocation and Pies */}
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
              percentage: portfolio?.totalValue ? (pie.totalValue / portfolio.totalValue) * 100 : 0
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
    </div>
  );
};

export default Dashboard;