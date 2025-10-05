import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Brush
} from 'recharts';
import { format, parseISO } from 'date-fns';
import ChartLoadingSkeleton from './ChartLoadingSkeleton';

export interface LineChartDataPoint {
  date: string;
  [key: string]: string | number;
}

export interface LineConfig {
  key: string;
  name: string;
  color: string;
  strokeWidth?: number;
  strokeDasharray?: string;
  visible?: boolean;
}

interface InteractiveLineChartProps {
  data: LineChartDataPoint[];
  lines: LineConfig[];
  loading?: boolean;
  height?: number;
  title?: string;
  yAxisLabel?: string;
  showGrid?: boolean;
  showBrush?: boolean;
  showLegend?: boolean;
  formatValue?: (value: number) => string;
  formatDate?: (date: string) => string;
  onLineToggle?: (lineKey: string, visible: boolean) => void;
  onDataPointClick?: (point: LineChartDataPoint) => void;
  className?: string;
}

const InteractiveLineChart: React.FC<InteractiveLineChartProps> = ({
  data,
  lines,
  loading = false,
  height = 400,
  title,
  yAxisLabel,
  showGrid = true,
  showBrush = false,
  showLegend = true,
  formatValue = (value) => `${value.toFixed(2)}%`,
  formatDate = (date) => format(parseISO(date), 'MMM dd, yyyy'),
  onLineToggle,
  onDataPointClick,
  className = ''
}) => {
  const [visibleLines, setVisibleLines] = useState<Set<string>>(
    new Set(lines.filter(line => line.visible !== false).map(line => line.key))
  );
  const [hoveredLine, setHoveredLine] = useState<string | null>(null);

  const handleLegendClick = useCallback((lineKey: string) => {
    const newVisibleLines = new Set(visibleLines);
    const isVisible = visibleLines.has(lineKey);
    
    if (isVisible) {
      newVisibleLines.delete(lineKey);
    } else {
      newVisibleLines.add(lineKey);
    }
    
    setVisibleLines(newVisibleLines);
    onLineToggle?.(lineKey, !isVisible);
  }, [visibleLines, onLineToggle]);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.8, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.8, y: 10 }}
          className="bg-white/95 backdrop-blur-md border border-gray-200 rounded-lg shadow-lg p-4 max-w-xs"
        >
          <p className="text-sm font-semibold text-gray-900 mb-2">
            {formatDate(label)}
          </p>
          <div className="space-y-1">
            {payload
              .filter((entry: any) => visibleLines.has(entry.dataKey))
              .map((entry: any, index: number) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: entry.color }}
                    />
                    <span className="text-sm text-gray-600">{entry.name}</span>
                  </div>
                  <span 
                    className="text-sm font-medium"
                    style={{ color: entry.color }}
                  >
                    {formatValue(entry.value)}
                  </span>
                </div>
              ))}
          </div>
        </motion.div>
      );
    }
    return null;
  };

  const CustomLegend = ({ payload }: any) => {
    if (!showLegend) return null;

    return (
      <div className="flex flex-wrap justify-center gap-4 mt-4">
        {payload.map((entry: any, index: number) => {
          const isVisible = visibleLines.has(entry.dataKey);
          const isHovered = hoveredLine === entry.dataKey;
          
          return (
            <motion.button
              key={index}
              onClick={() => handleLegendClick(entry.dataKey)}
              onMouseEnter={() => setHoveredLine(entry.dataKey)}
              onMouseLeave={() => setHoveredLine(null)}
              className={`flex items-center space-x-2 px-3 py-1 rounded-full transition-all duration-200 ${
                isVisible 
                  ? 'bg-white/80 backdrop-blur-sm border border-gray-200 shadow-sm' 
                  : 'bg-gray-100 border border-gray-300'
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <motion.div
                className="w-3 h-3 rounded-full"
                style={{ 
                  backgroundColor: isVisible ? entry.color : '#9ca3af',
                  opacity: isVisible ? 1 : 0.5
                }}
                animate={{
                  scale: isHovered ? 1.2 : 1,
                  transition: { type: "spring", stiffness: 300, damping: 20 }
                }}
              />
              <span 
                className={`text-sm font-medium transition-colors ${
                  isVisible ? 'text-gray-900' : 'text-gray-500'
                }`}
              >
                {entry.value}
              </span>
            </motion.button>
          );
        })}
      </div>
    );
  };

  const CustomDot = (props: any) => {
    const { cx, cy, payload, dataKey } = props;
    const lineConfig = lines.find(line => line.key === dataKey);
    
    if (!visibleLines.has(dataKey) || !lineConfig) return null;
    
    return (
      <motion.circle
        cx={cx}
        cy={cy}
        r={3}
        fill={lineConfig.color}
        stroke="white"
        strokeWidth={2}
        className="cursor-pointer"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.5, r: 5 }}
        whileTap={{ scale: 0.8 }}
        onClick={() => onDataPointClick && onDataPointClick(payload)}
      />
    );
  };

  if (loading) {
    return <ChartLoadingSkeleton height={height} type="line" showLegend={showLegend} />;
  }

  if (!data || data.length === 0) {
    return (
      <div 
        className={`flex items-center justify-center bg-gray-50 rounded-lg border border-gray-200 ${className}`}
        style={{ height }}
      >
        <div className="text-center">
          <div className="text-gray-400 text-lg mb-2">📊</div>
          <p className="text-gray-500 font-medium">No comparison data available</p>
          <p className="text-gray-400 text-sm">Benchmark data will appear here</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`bg-white/50 backdrop-blur-sm rounded-lg border border-gray-200 p-4 ${className}`}
    >
      {title && (
        <motion.h3
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-lg font-semibold text-gray-900 mb-4"
        >
          {title}
        </motion.h3>
      )}
      
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{ top: 5, right: 30, left: 20, bottom: showBrush ? 60 : 5 }}
          >
            {showGrid && (
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke="#e5e7eb"
                opacity={0.5}
              />
            )}
            
            <XAxis
              dataKey="date"
              tickFormatter={(date) => format(parseISO(date), 'MMM dd')}
              stroke="#6b7280"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            
            <YAxis
              tickFormatter={formatValue}
              stroke="#6b7280"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              label={yAxisLabel ? { 
                value: yAxisLabel, 
                angle: -90, 
                position: 'insideLeft',
                style: { textAnchor: 'middle' }
              } : undefined}
            />
            
            <Tooltip 
              content={<CustomTooltip />}
              cursor={{ stroke: '#6b7280', strokeWidth: 1, strokeDasharray: '3 3' }}
            />
            
            {showLegend && <Legend content={<CustomLegend />} />}
            
            {/* Zero reference line */}
            <ReferenceLine 
              y={0} 
              stroke="#6b7280" 
              strokeDasharray="2 2"
              opacity={0.3}
            />
            
            {lines.map((lineConfig) => (
              <Line
                key={lineConfig.key}
                type="monotone"
                dataKey={lineConfig.key}
                name={lineConfig.name}
                stroke={lineConfig.color}
                strokeWidth={lineConfig.strokeWidth || 2}
                strokeDasharray={lineConfig.strokeDasharray}
                dot={<CustomDot />}
                activeDot={{ 
                  r: 6, 
                  stroke: lineConfig.color, 
                  strokeWidth: 2, 
                  fill: 'white' 
                }}
                hide={!visibleLines.has(lineConfig.key)}
                animationDuration={1000}
                animationEasing="ease-out"
                connectNulls={false}
              />
            ))}
            
            {showBrush && (
              <Brush
                dataKey="date"
                height={30}
                stroke="#3B82F6"
                tickFormatter={(date) => format(parseISO(date), 'MMM')}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
};

export default InteractiveLineChart;