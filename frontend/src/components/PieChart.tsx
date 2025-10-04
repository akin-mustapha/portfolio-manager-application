import React from 'react';

interface PieChartData {
  name: string;
  value: number;
  percentage: number;
}

interface PieChartProps {
  data: PieChartData[];
  loading?: boolean;
  height?: number;
}

const PieChart: React.FC<PieChartProps> = ({ 
  data, 
  loading = false, 
  height = 300 
}) => {
  // Generate colors for pie slices
  const colors = [
    '#3B82F6', // blue-500
    '#10B981', // emerald-500
    '#F59E0B', // amber-500
    '#EF4444', // red-500
    '#8B5CF6', // violet-500
    '#06B6D4', // cyan-500
    '#84CC16', // lime-500
    '#F97316', // orange-500
    '#EC4899', // pink-500
    '#6B7280', // gray-500
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <div className="animate-pulse">
          <div className="w-48 h-48 bg-gray-200 rounded-full"></div>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center" style={{ height }}>
        <div className="text-center">
          <div className="text-gray-400 text-4xl mb-2">📊</div>
          <p className="text-gray-500 font-medium">No portfolio data available</p>
          <p className="text-gray-400 text-sm mt-1">
            Connect your Trading 212 API to view allocation
          </p>
        </div>
      </div>
    );
  }

  // Calculate angles for pie slices
  const total = data.reduce((sum, item) => sum + item.value, 0);
  let currentAngle = 0;
  
  const slices = data.map((item, index) => {
    const percentage = (item.value / total) * 100;
    const angle = (item.value / total) * 360;
    const startAngle = currentAngle;
    currentAngle += angle;
    
    return {
      ...item,
      percentage,
      angle,
      startAngle,
      color: colors[index % colors.length]
    };
  });

  // SVG pie chart implementation
  const radius = 80;
  const centerX = 100;
  const centerY = 100;

  const createPath = (startAngle: number, angle: number) => {
    const start = (startAngle * Math.PI) / 180;
    const end = ((startAngle + angle) * Math.PI) / 180;
    
    const x1 = centerX + radius * Math.cos(start);
    const y1 = centerY + radius * Math.sin(start);
    const x2 = centerX + radius * Math.cos(end);
    const y2 = centerY + radius * Math.sin(end);
    
    const largeArc = angle > 180 ? 1 : 0;
    
    return `M ${centerX} ${centerY} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`;
  };

  return (
    <div className="space-y-4">
      {/* SVG Pie Chart */}
      <div className="flex justify-center">
        <svg width="200" height="200" viewBox="0 0 200 200">
          {slices.map((slice, index) => (
            <g key={index}>
              <path
                d={createPath(slice.startAngle, slice.angle)}
                fill={slice.color}
                stroke="white"
                strokeWidth="2"
                className="hover:opacity-80 transition-opacity cursor-pointer"
              />
              <title>{`${slice.name}: ${slice.percentage.toFixed(1)}%`}</title>
            </g>
          ))}
        </svg>
      </div>

      {/* Legend */}
      <div className="space-y-2 max-h-48 overflow-y-auto">
        {slices.map((slice, index) => (
          <div key={index} className="flex items-center justify-between text-sm hover:bg-gray-50 p-1 rounded">
            <div className="flex items-center space-x-2 flex-1 min-w-0">
              <div 
                className="w-3 h-3 rounded-full flex-shrink-0"
                style={{ backgroundColor: slice.color }}
              />
              <span className="text-gray-700 truncate" title={slice.name}>
                {slice.name}
              </span>
            </div>
            <div className="flex items-center space-x-3 text-gray-500 flex-shrink-0">
              <span className="font-medium text-gray-900">{slice.percentage.toFixed(1)}%</span>
              <span className="text-xs">£{slice.value.toLocaleString()}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Total */}
      <div className="border-t pt-2">
        <div className="flex items-center justify-between text-sm font-medium">
          <span className="text-gray-700">Total Portfolio</span>
          <span className="text-gray-900">£{total.toLocaleString()}</span>
        </div>
        {data.length > 0 && (
          <div className="text-xs text-gray-400 mt-1 text-center">
            {data.length} pie{data.length !== 1 ? 's' : ''} • Live allocation
          </div>
        )}
      </div>
    </div>
  );
};

export default PieChart;