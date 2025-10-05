import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { format, parseISO } from 'date-fns';
import ChartLoadingSkeleton from './ChartLoadingSkeleton';

export interface TimeSeriesDataPoint {
  date: string;
  value: number;
  label?: string;
}

interface AnimatedTimeSeriesChartProps {
  data: TimeSeriesDataPoint[];
  loading?: boolean;
  height?: number;
  color?: string;
  title?: string;
  yAxisLabel?: string;
  showGrid?: boolean;
  showTooltip?: boolean;
  animationDuration?: number;
  formatValue?: (value: number) => string;
  formatDate?: (date: string) => string;
  onPointClick?: (point: TimeSeriesDataPoint) => void;
  className?: string;
}

const AnimatedTimeSeriesChart: React.FC<AnimatedTimeSeriesChartProps> = ({
  data,
  loading = false,
  height = 300,
  color = '#3B82F6',
  title,
  yAxisLabel,
  showGrid = true,
  showTooltip = true,
  animationDuration = 1000,
  formatValue = (value) => value.toLocaleString(),
  formatDate = (date) => format(parseISO(date), 'MMM dd'),
  onPointClick,
  className = ''
}) => {
  const [animatedData, setAnimatedData] = useState<TimeSeriesDataPoint[]>([]);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (data.length > 0 && !loading) {
      setIsAnimating(true);
      
      // Animate data points in sequence
      const animatePoints = async () => {
        const newData: TimeSeriesDataPoint[] = [];
        
        for (let i = 0; i < data.length; i++) {
          newData.push(data[i]);
          setAnimatedData([...newData]);
          
          // Delay between points for smooth animation
          if (i < data.length - 1) {
            await new Promise(resolve => setTimeout(resolve, animationDuration / data.length));
          }
        }
        
        setIsAnimating(false);
      };
      
      animatePoints();
    }
  }, [data, loading, animationDuration]);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          className="bg-white/95 backdrop-blur-md border border-gray-200 rounded-lg shadow-lg p-3"
        >
          <p className="text-sm font-medium text-gray-900">
            {formatDate(label)}
          </p>
          <p className="text-sm text-gray-600">
            {yAxisLabel && `${yAxisLabel}: `}
            <span className="font-semibold" style={{ color }}>
              {formatValue(payload[0].value)}
            </span>
          </p>
          {data.label && (
            <p className="text-xs text-gray-500 mt-1">{data.label}</p>
          )}
        </motion.div>
      );
    }
    return null;
  };

  const CustomDot = (props: any) => {
    const { cx, cy, payload, index } = props;
    
    return (
      <motion.circle
        cx={cx}
        cy={cy}
        r={4}
        fill={color}
        stroke="white"
        strokeWidth={2}
        className="cursor-pointer hover:r-6 transition-all duration-200"
        initial={{ scale: 0, opacity: 0 }}
        animate={{ 
          scale: 1, 
          opacity: 1,
          transition: { 
            delay: index * (animationDuration / 1000) / data.length,
            type: "spring",
            stiffness: 300,
            damping: 20
          }
        }}
        whileHover={{ scale: 1.5 }}
        whileTap={{ scale: 0.9 }}
        onClick={() => onPointClick && onPointClick(payload)}
      />
    );
  };

  if (loading) {
    return <ChartLoadingSkeleton height={height} type="timeseries" />;
  }

  if (!data || data.length === 0) {
    return (
      <div 
        className={`flex items-center justify-center bg-gray-50 rounded-lg border border-gray-200 ${className}`}
        style={{ height }}
      >
        <div className="text-center">
          <div className="text-gray-400 text-lg mb-2">📈</div>
          <p className="text-gray-500 font-medium">No data available</p>
          <p className="text-gray-400 text-sm">Time series data will appear here</p>
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
            data={animatedData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
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
              tickFormatter={formatDate}
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
            
            {showTooltip && (
              <Tooltip 
                content={<CustomTooltip />}
                cursor={{ stroke: color, strokeWidth: 1, strokeDasharray: '3 3' }}
              />
            )}
            
            <Line
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={2}
              dot={<CustomDot />}
              activeDot={{ 
                r: 6, 
                stroke: color, 
                strokeWidth: 2, 
                fill: 'white' 
              }}
              animationDuration={animationDuration}
              animationEasing="ease-out"
            />
            
            {/* Zero reference line if data crosses zero */}
            {data.some(d => d.value < 0) && data.some(d => d.value > 0) && (
              <ReferenceLine 
                y={0} 
                stroke="#6b7280" 
                strokeDasharray="2 2"
                opacity={0.5}
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      {isAnimating && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute bottom-2 right-2"
        >
          <div className="flex items-center space-x-2 text-xs text-gray-500">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
            <span>Loading data...</span>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default AnimatedTimeSeriesChart;