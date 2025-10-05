import React, { useState, useCallback, useRef } from 'react';
import { motion, PanInfo } from 'framer-motion';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Cell
} from 'recharts';
import ChartLoadingSkeleton from './ChartLoadingSkeleton';

export interface ScatterDataPoint {
  x: number;
  y: number;
  size?: number;
  label: string;
  category?: string;
  color?: string;
  metadata?: Record<string, any>;
}

interface AnimatedScatterChartProps {
  data: ScatterDataPoint[];
  loading?: boolean;
  height?: number;
  title?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  showGrid?: boolean;
  enableZoom?: boolean;
  enablePan?: boolean;
  formatXValue?: (value: number) => string;
  formatYValue?: (value: number) => string;
  onPointClick?: (point: ScatterDataPoint) => void;
  onPointHover?: (point: ScatterDataPoint | null) => void;
  className?: string;
  colorScheme?: string[];
}

const AnimatedScatterChart: React.FC<AnimatedScatterChartProps> = ({
  data,
  loading = false,
  height = 400,
  title,
  xAxisLabel = 'Risk (Volatility %)',
  yAxisLabel = 'Return %',
  showGrid = true,
  enableZoom = true,
  enablePan = true,
  formatXValue = (value) => `${value.toFixed(1)}%`,
  formatYValue = (value) => `${value.toFixed(1)}%`,
  onPointClick,
  onPointHover,
  className = '',
  colorScheme = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4']
}) => {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [hoveredPoint, setHoveredPoint] = useState<ScatterDataPoint | null>(null);
  const chartRef = useRef<HTMLDivElement>(null);

  // Calculate data bounds for zoom/pan limits
  const dataBounds = React.useMemo(() => {
    if (!data.length) return { minX: 0, maxX: 100, minY: -10, maxY: 10 };
    
    const xValues = data.map(d => d.x);
    const yValues = data.map(d => d.y);
    
    return {
      minX: Math.min(...xValues) - 1,
      maxX: Math.max(...xValues) + 1,
      minY: Math.min(...yValues) - 1,
      maxY: Math.max(...yValues) + 1
    };
  }, [data]);

  const handleWheel = useCallback((event: React.WheelEvent) => {
    if (!enableZoom) return;
    
    event.preventDefault();
    const delta = event.deltaY > 0 ? 0.9 : 1.1;
    setZoomLevel(prev => Math.max(0.5, Math.min(5, prev * delta)));
  }, [enableZoom]);

  const handlePanStart = useCallback(() => {
    if (chartRef.current) {
      chartRef.current.style.cursor = 'grabbing';
    }
  }, []);

  const handlePan = useCallback((event: MouseEvent, info: PanInfo) => {
    if (!enablePan) return;
    
    setPanOffset(prev => ({
      x: prev.x + info.delta.x,
      y: prev.y + info.delta.y
    }));
  }, [enablePan]);

  const handlePanEnd = useCallback(() => {
    if (chartRef.current) {
      chartRef.current.style.cursor = enablePan ? 'grab' : 'default';
    }
  }, [enablePan]);

  const resetZoomPan = useCallback(() => {
    setZoomLevel(1);
    setPanOffset({ x: 0, y: 0 });
  }, []);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const point = payload[0].payload as ScatterDataPoint;
      
      return (
        <motion.div
          initial={{ opacity: 0, scale: 0.8, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.8, y: 10 }}
          className="bg-white/95 backdrop-blur-md border border-gray-200 rounded-lg shadow-lg p-4 max-w-xs"
        >
          <p className="text-sm font-semibold text-gray-900 mb-2">
            {point.label}
          </p>
          <div className="space-y-1">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">{xAxisLabel}:</span>
              <span className="text-sm font-medium text-gray-900">
                {formatXValue(point.x)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">{yAxisLabel}:</span>
              <span className="text-sm font-medium text-gray-900">
                {formatYValue(point.y)}
              </span>
            </div>
            {point.category && (
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Category:</span>
                <span className="text-sm font-medium text-gray-900">
                  {point.category}
                </span>
              </div>
            )}
            {point.metadata && Object.entries(point.metadata).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="text-sm text-gray-600 capitalize">{key}:</span>
                <span className="text-sm font-medium text-gray-900">
                  {typeof value === 'number' ? value.toLocaleString() : String(value)}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      );
    }
    return null;
  };

  const CustomDot = (props: any) => {
    const { cx, cy, payload, index } = props;
    const point = payload as ScatterDataPoint;
    const color = point.color || colorScheme[index % colorScheme.length];
    const size = point.size || 8;
    
    return (
      <motion.g
        initial={{ scale: 0, opacity: 0 }}
        animate={{ 
          scale: 1, 
          opacity: 1,
          transition: { 
            delay: index * 0.05,
            type: "spring",
            stiffness: 300,
            damping: 20
          }
        }}
      >
        <motion.circle
          cx={cx}
          cy={cy}
          r={size}
          fill={color}
          stroke="white"
          strokeWidth={2}
          className="cursor-pointer"
          whileHover={{ 
            scale: 1.3,
            transition: { type: "spring", stiffness: 400, damping: 10 }
          }}
          whileTap={{ scale: 0.9 }}
          onMouseEnter={() => {
            setHoveredPoint(point);
            onPointHover?.(point);
          }}
          onMouseLeave={() => {
            setHoveredPoint(null);
            onPointHover?.(null);
          }}
          onClick={() => onPointClick?.(point)}
        />
        
        {/* Point label on hover */}
        {hoveredPoint === point && (
          <motion.text
            x={cx}
            y={cy - size - 8}
            textAnchor="middle"
            className="text-xs font-medium fill-gray-900 pointer-events-none"
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 5 }}
          >
            {point.label}
          </motion.text>
        )}
      </motion.g>
    );
  };

  if (loading) {
    return <ChartLoadingSkeleton height={height} type="scatter" />;
  }

  if (!data || data.length === 0) {
    return (
      <div 
        className={`flex items-center justify-center bg-gray-50 rounded-lg border border-gray-200 ${className}`}
        style={{ height }}
      >
        <div className="text-center">
          <div className="text-gray-400 text-lg mb-2">🎯</div>
          <p className="text-gray-500 font-medium">No risk-return data available</p>
          <p className="text-gray-400 text-sm">Scatter plot will appear here</p>
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
        <div className="flex items-center justify-between mb-4">
          <motion.h3
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-lg font-semibold text-gray-900"
          >
            {title}
          </motion.h3>
          
          {(enableZoom || enablePan) && (
            <div className="flex items-center space-x-2">
              <span className="text-xs text-gray-500">
                Zoom: {(zoomLevel * 100).toFixed(0)}%
              </span>
              <motion.button
                onClick={resetZoomPan}
                className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Reset
              </motion.button>
            </div>
          )}
        </div>
      )}
      
      <motion.div
        ref={chartRef}
        style={{ height, cursor: enablePan ? 'grab' : 'default' }}
        onWheel={handleWheel}
        drag={enablePan}
        onDragStart={handlePanStart}
        onDrag={handlePan}
        onDragEnd={handlePanEnd}
        dragConstraints={{ left: -100, right: 100, top: -100, bottom: 100 }}
      >
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart
            data={data}
            margin={{ top: 20, right: 30, bottom: 40, left: 40 }}
          >
            {showGrid && (
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke="#e5e7eb"
                opacity={0.5}
              />
            )}
            
            <XAxis
              type="number"
              dataKey="x"
              domain={[dataBounds.minX, dataBounds.maxX]}
              tickFormatter={formatXValue}
              stroke="#6b7280"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              label={{ 
                value: xAxisLabel, 
                position: 'insideBottom', 
                offset: -10,
                style: { textAnchor: 'middle' }
              }}
            />
            
            <YAxis
              type="number"
              dataKey="y"
              domain={[dataBounds.minY, dataBounds.maxY]}
              tickFormatter={formatYValue}
              stroke="#6b7280"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              label={{ 
                value: yAxisLabel, 
                angle: -90, 
                position: 'insideLeft',
                style: { textAnchor: 'middle' }
              }}
            />
            
            <Tooltip 
              content={<CustomTooltip />}
              cursor={{ strokeDasharray: '3 3' }}
            />
            
            {/* Reference lines for zero */}
            <ReferenceLine 
              x={0} 
              stroke="#6b7280" 
              strokeDasharray="2 2"
              opacity={0.3}
            />
            <ReferenceLine 
              y={0} 
              stroke="#6b7280" 
              strokeDasharray="2 2"
              opacity={0.3}
            />
            
            <Scatter
              data={data}
              shape={<CustomDot />}
            />
          </ScatterChart>
        </ResponsiveContainer>
      </motion.div>
      
      {(enableZoom || enablePan) && (
        <div className="mt-2 text-xs text-gray-500 text-center">
          {enableZoom && 'Scroll to zoom'} 
          {enableZoom && enablePan && ' • '}
          {enablePan && 'Drag to pan'}
        </div>
      )}
    </motion.div>
  );
};

export default AnimatedScatterChart;