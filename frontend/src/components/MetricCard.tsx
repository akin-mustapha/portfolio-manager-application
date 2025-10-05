import React from 'react';
import { Icon } from './icons';

interface TrendData {
  value: number;
  isPositive: boolean;
  prefix?: string;
  suffix?: string;
}

interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
  loading?: boolean;
  trend?: TrendData;
  icon?: string | React.ReactNode;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  loading = false,
  trend,
  icon
}) => {
  const formatTrendValue = (trend: TrendData) => {
    const prefix = trend.prefix || '';
    const suffix = trend.suffix || '';
    const formattedValue = Math.abs(trend.value).toLocaleString();
    return `${prefix}${formattedValue}${suffix}`;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-3"></div>
          <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
          {title}
        </h3>
        {icon && (
          <div className="text-gray-400">
            {typeof icon === 'string' ? <span className="text-2xl">{icon}</span> : icon}
          </div>
        )}
      </div>
      
      <div className="flex items-baseline space-x-2">
        <p className="text-2xl font-bold text-gray-900">
          {value}
        </p>
        
        {trend && (
          <div className={`flex items-center text-sm font-medium ${
            trend.isPositive ? 'text-green-600' : 'text-red-600'
          }`}>
            <span className="mr-1">
              <Icon 
                name={trend.isPositive ? 'ArrowUpRight' : 'ArrowDownRight'} 
                size="sm" 
              />
            </span>
            {formatTrendValue(trend)}
          </div>
        )}
      </div>
      
      {subtitle && (
        <p className="text-sm text-gray-500 mt-1">
          {subtitle}
        </p>
      )}
    </div>
  );
};

export default MetricCard;