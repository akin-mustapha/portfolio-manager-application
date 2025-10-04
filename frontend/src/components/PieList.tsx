import React from 'react';
import { Link } from 'react-router-dom';
import { Pie } from '../types';

interface PieListProps {
  pies: Pie[];
  loading?: boolean;
  maxItems?: number;
  showViewAll?: boolean;
}

const PieList: React.FC<PieListProps> = ({ 
  pies, 
  loading = false, 
  maxItems,
  showViewAll = true
}) => {
  if (loading) {
    return (
      <div className="space-y-3">
        {[...Array(3)].map((_, index) => (
          <div key={index} className="animate-pulse">
            <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/4"></div>
              </div>
              <div className="text-right">
                <div className="h-4 bg-gray-200 rounded w-16 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-12"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!pies || pies.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-400 text-4xl mb-2">🥧</div>
        <p className="text-gray-500">No pies found</p>
        <p className="text-sm text-gray-400 mt-1">
          Create pies in your Trading 212 account to see them here
        </p>
      </div>
    );
  }

  const displayPies = maxItems ? pies.slice(0, maxItems) : pies;
  const hasMore = maxItems && pies.length > maxItems;

  const formatReturn = (pie: Pie) => {
    // Calculate return amount from percentage and invested amount
    const returnAmount = (pie.returnPct / 100) * pie.investedAmount;
    const isPositive = returnAmount >= 0;
    const color = isPositive ? 'text-green-600' : 'text-red-600';
    const sign = isPositive ? '+' : '';
    
    return (
      <div className={`text-right ${color}`}>
        <div className="font-medium">
          {sign}£{Math.abs(returnAmount).toLocaleString()}
        </div>
        <div className="text-sm">
          {sign}{pie.returnPct.toFixed(2)}%
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-3">
      {displayPies.map((pie) => (
        <div
          key={pie.id}
          className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:border-gray-300 hover:shadow-sm transition-all cursor-pointer"
        >
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <h4 className="font-medium text-gray-900 truncate">
                {pie.name}
              </h4>
              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                {pie.totalValue > 0 ? 'Active' : 'Empty'}
              </span>
            </div>
            <div className="flex items-center space-x-4 mt-1 text-sm text-gray-500">
              <span>Value: £{pie.totalValue.toLocaleString()}</span>
              <span>•</span>
              <span>Invested: £{pie.investedAmount.toLocaleString()}</span>
              {pie.updatedAt && (
                <>
                  <span>•</span>
                  <span>Updated: {new Date(pie.updatedAt).toLocaleDateString()}</span>
                </>
              )}
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            {formatReturn(pie)}
            <div className="text-gray-400">
              →
            </div>
          </div>
        </div>
      ))}

      {hasMore && showViewAll && (
        <div className="pt-3 border-t">
          <Link
            to="/pie-analysis"
            className="block text-center text-blue-600 hover:text-blue-800 text-sm font-medium py-2"
          >
            View all {pies.length} pies →
          </Link>
        </div>
      )}

      {!hasMore && pies.length > 3 && showViewAll && (
        <div className="pt-3 border-t">
          <Link
            to="/pie-analysis"
            className="block text-center text-blue-600 hover:text-blue-800 text-sm font-medium py-2"
          >
            View detailed analysis →
          </Link>
        </div>
      )}
    </div>
  );
};

export default PieList;