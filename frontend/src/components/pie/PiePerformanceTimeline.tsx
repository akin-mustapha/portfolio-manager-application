import React, { useState, useMemo, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Area, AreaChart } from 'recharts';
import { format, subDays, subMonths, subYears, parseISO } from 'date-fns';
import { Pie } from '../../types/api';
import { Icon } from '../icons';
import { Button } from '../ui/Button';
import AnimatedTimeSeriesChart, { TimeSeriesDataPoint } from '../charts/AnimatedTimeSeriesChart';
import { containerVariants, listItemVariants, springTransition } from '../../utils/animations';

interface PiePerformanceTimelineProps {
  pie: Pie | null;
  loading?: boolean;
  onTimeRangeChange?: (range: TimeRange) => void;
}

type TimeRange = '1D' | '1W' | '1M' | '3M' | '6M' | '1Y' | '2Y' | 'ALL';
type MetricType = 'value' | 'return' | 'returnPct' | 'benchmark';

interface TimelineDataPoint extends TimeSeriesDataPoint {
  value: number;
  returnPct: number;
  benchmarkValue?: number;
  volume?: number;
  dividends?: number;
}

interface ScrubbingState {
  isActive: boolean;
  position: number;
  dataIndex: number;
  timestamp: string;
}

const PiePerformanceTimeline: React.FC<PiePerformanceTimelineProps> = ({
  pie,
  loading = false,
  onTimeRangeChange
}) => {
  const [timeRange, setTimeRange] = useState<TimeRange>('6M');
  const [metricType, setMetricType] = useState<MetricType>('value');
  const [showBenchmark, setShowBenchmark] = useState(true);
  const [scrubbing, setScrubbing] = useState<ScrubbingState>({
    isActive: false,
    position: 0,
    dataIndex: 0,
    timestamp: ''
  });
  const [selectedDataPoint, setSelectedDataPoint] = useState<TimelineDataPoint | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  
  const chartRef = useRef<HTMLDivElement>(null);
  const playbackRef = useRef<NodeJS.Timeout>();

  // Generate mock historical data
  const timelineData = useMemo((): TimelineDataPoint[] => {
    if (!pie) return [];

    const now = new Date();
    const getDaysBack = (range: TimeRange): number => {
      switch (range) {
        case '1D': return 1;
        case '1W': return 7;
        case '1M': return 30;
        case '3M': return 90;
        case '6M': return 180;
        case '1Y': return 365;
        case '2Y': return 730;
        case 'ALL': return 1095; // 3 years
        default: return 180;
      }
    };

    const days = getDaysBack(timeRange);
    const dataPoints: TimelineDataPoint[] = [];
    const startValue = pie.investedAmount;
    const endValue = pie.totalValue;
    const totalReturn = (endValue - startValue) / startValue;

    for (let i = days; i >= 0; i--) {
      const date = subDays(now, i);
      const progress = (days - i) / days;
      
      // Add some realistic volatility
      const volatility = 0.15; // 15% annual volatility
      const dailyVolatility = volatility / Math.sqrt(252); // Convert to daily
      const randomFactor = 1 + (Math.random() - 0.5) * dailyVolatility * 2;
      
      // Calculate progressive value with some noise
      const progressiveReturn = totalReturn * progress;
      const value = startValue * (1 + progressiveReturn) * randomFactor;
      const returnPct = ((value - startValue) / startValue) * 100;
      
      // Mock benchmark data (slightly different performance)
      const benchmarkReturn = progressiveReturn * 0.8 + (Math.random() - 0.5) * 0.02;
      const benchmarkValue = startValue * (1 + benchmarkReturn);
      
      dataPoints.push({
        date: date.toISOString(),
        value: Math.max(value, startValue * 0.7), // Prevent unrealistic losses
        returnPct,
        benchmarkValue,
        volume: Math.floor(Math.random() * 1000000) + 500000,
        dividends: Math.random() < 0.05 ? Math.random() * 100 + 10 : 0, // 5% chance of dividend
        label: `${format(date, 'MMM dd, yyyy')}: £${value.toLocaleString()}`
      });
    }

    return dataPoints;
  }, [pie, timeRange]);

  const timeRangeOptions = [
    { value: '1D' as TimeRange, label: '1D' },
    { value: '1W' as TimeRange, label: '1W' },
    { value: '1M' as TimeRange, label: '1M' },
    { value: '3M' as TimeRange, label: '3M' },
    { value: '6M' as TimeRange, label: '6M' },
    { value: '1Y' as TimeRange, label: '1Y' },
    { value: '2Y' as TimeRange, label: '2Y' },
    { value: 'ALL' as TimeRange, label: 'ALL' }
  ];

  const metricOptions = [
    { value: 'value' as MetricType, label: 'Portfolio Value', icon: 'DollarSign' },
    { value: 'return' as MetricType, label: 'Absolute Return', icon: 'TrendingUp' },
    { value: 'returnPct' as MetricType, label: 'Return %', icon: 'Percent' },
    { value: 'benchmark' as MetricType, label: 'vs Benchmark', icon: 'BarChart3' }
  ];

  const handleTimeRangeChange = (range: TimeRange) => {
    setTimeRange(range);
    onTimeRangeChange?.(range);
  };

  const handleMouseMove = (event: React.MouseEvent<HTMLDivElement>) => {
    if (!chartRef.current || timelineData.length === 0) return;

    const rect = chartRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const width = rect.width;
    const position = Math.max(0, Math.min(1, x / width));
    const dataIndex = Math.floor(position * (timelineData.length - 1));
    const dataPoint = timelineData[dataIndex];

    if (dataPoint) {
      setScrubbing({
        isActive: true,
        position: position * 100,
        dataIndex,
        timestamp: dataPoint.date
      });
      setSelectedDataPoint(dataPoint);
    }
  };

  const handleMouseLeave = () => {
    setScrubbing(prev => ({ ...prev, isActive: false }));
    setSelectedDataPoint(null);
  };

  const startPlayback = () => {
    if (isPlaying) {
      if (playbackRef.current) {
        clearInterval(playbackRef.current);
      }
      setIsPlaying(false);
      return;
    }

    setIsPlaying(true);
    let currentIndex = 0;

    playbackRef.current = setInterval(() => {
      if (currentIndex >= timelineData.length - 1) {
        setIsPlaying(false);
        if (playbackRef.current) {
          clearInterval(playbackRef.current);
        }
        return;
      }

      const dataPoint = timelineData[currentIndex];
      const position = (currentIndex / (timelineData.length - 1)) * 100;

      setScrubbing({
        isActive: true,
        position,
        dataIndex: currentIndex,
        timestamp: dataPoint.date
      });
      setSelectedDataPoint(dataPoint);

      currentIndex++;
    }, 1000 / playbackSpeed);
  };

  useEffect(() => {
    return () => {
      if (playbackRef.current) {
        clearInterval(playbackRef.current);
      }
    };
  }, []);

  const getChartData = () => {
    switch (metricType) {
      case 'return':
        return timelineData.map(d => ({ ...d, value: d.value - (pie?.investedAmount || 0) }));
      case 'returnPct':
        return timelineData.map(d => ({ ...d, value: d.returnPct }));
      case 'benchmark':
        return timelineData.map(d => ({ ...d, value: d.value, benchmark: d.benchmarkValue }));
      default:
        return timelineData;
    }
  };

  const formatValue = (value: number): string => {
    switch (metricType) {
      case 'returnPct':
        return `${value.toFixed(2)}%`;
      case 'return':
        return `£${value.toLocaleString()}`;
      default:
        return `£${value.toLocaleString()}`;
    }
  };

  const getMetricColor = (): string => {
    if (!selectedDataPoint && !pie) return '#3B82F6';
    
    const currentValue = selectedDataPoint?.value || pie?.totalValue || 0;
    const investedAmount = pie?.investedAmount || 0;
    
    return currentValue >= investedAmount ? '#10B981' : '#EF4444';
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
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
          <Icon name="LineChart" size="2xl" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Select a Pie to View Timeline
        </h3>
        <p className="text-gray-600">
          Choose a pie to see its historical performance timeline.
        </p>
      </motion.div>
    );
  }

  const chartData = getChartData();

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4"
      >
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Performance Timeline: {pie.name}
          </h2>
          <p className="text-gray-600">
            Interactive historical performance analysis with scrubbing controls
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          {/* Metric Type Selector */}
          <select
            value={metricType}
            onChange={(e) => setMetricType(e.target.value as MetricType)}
            className="px-4 py-2 border border-gray-300 rounded-lg bg-white/80 backdrop-blur-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {metricOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          {/* Time Range Selector */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            {timeRangeOptions.map((option) => (
              <motion.button
                key={option.value}
                onClick={() => handleTimeRangeChange(option.value)}
                className={`
                  px-3 py-2 rounded-md text-sm font-medium transition-all duration-200
                  ${timeRange === option.value
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                  }
                `}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {option.label}
              </motion.button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Current Value Display */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white"
      >
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm text-blue-100 mb-1">
              {selectedDataPoint 
                ? format(parseISO(selectedDataPoint.date), 'MMM dd, yyyy HH:mm')
                : 'Current Value'
              }
            </div>
            <div className="text-3xl font-bold">
              {formatValue(selectedDataPoint?.value || pie.totalValue)}
            </div>
            <div className="text-blue-100 mt-1">
              {selectedDataPoint 
                ? `Return: ${selectedDataPoint.returnPct.toFixed(2)}%`
                : `Total Return: ${pie.returnPercentage.toFixed(2)}%`
              }
            </div>
          </div>
          
          {/* Playback Controls */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-blue-100">Speed:</span>
              <select
                value={playbackSpeed}
                onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
                className="px-2 py-1 rounded bg-white/20 text-white text-sm border-0 focus:ring-2 focus:ring-white/50"
              >
                <option value={0.5}>0.5x</option>
                <option value={1}>1x</option>
                <option value={2}>2x</option>
                <option value={4}>4x</option>
              </select>
            </div>
            
            <motion.button
              onClick={startPlayback}
              className="flex items-center space-x-2 px-4 py-2 bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Icon name={isPlaying ? 'X' : 'Play'} size="sm" />
              <span>{isPlaying ? 'Stop' : 'Play'}</span>
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* Main Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white/80 backdrop-blur-sm rounded-xl p-6 border border-gray-200 relative"
        ref={chartRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">
            {metricOptions.find(m => m.value === metricType)?.label}
          </h3>
          
          <div className="flex items-center space-x-4">
            <label className="flex items-center space-x-2 text-sm">
              <input
                type="checkbox"
                checked={showBenchmark}
                onChange={(e) => setShowBenchmark(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span>Show Benchmark</span>
            </label>
          </div>
        </div>

        <div className="h-96 relative">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={getMetricColor()} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={getMetricColor()} stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorBenchmark" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6B7280" stopOpacity={0.2}/>
                  <stop offset="95%" stopColor="#6B7280" stopOpacity={0}/>
                </linearGradient>
              </defs>
              
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.5} />
              
              <XAxis
                dataKey="date"
                tickFormatter={(date) => format(parseISO(date), timeRange === '1D' ? 'HH:mm' : 'MMM dd')}
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
              />
              
              <Tooltip
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-white/95 backdrop-blur-md border border-gray-200 rounded-lg shadow-lg p-4"
                      >
                        <p className="font-medium text-gray-900 mb-2">
                          {label ? format(parseISO(String(label)), 'MMM dd, yyyy HH:mm') : 'N/A'}
                        </p>
                        <div className="space-y-1">
                          <p className="text-sm">
                            <span className="text-gray-600">Value: </span>
                            <span className="font-medium">{formatValue(data.value)}</span>
                          </p>
                          <p className="text-sm">
                            <span className="text-gray-600">Return: </span>
                            <span className={`font-medium ${data.returnPct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {data.returnPct.toFixed(2)}%
                            </span>
                          </p>
                          {showBenchmark && data.benchmarkValue && (
                            <p className="text-sm">
                              <span className="text-gray-600">Benchmark: </span>
                              <span className="font-medium">£{data.benchmarkValue.toLocaleString()}</span>
                            </p>
                          )}
                          {data.dividends > 0 && (
                            <p className="text-sm">
                              <span className="text-gray-600">Dividend: </span>
                              <span className="font-medium text-green-600">£{data.dividends.toFixed(2)}</span>
                            </p>
                          )}
                        </div>
                      </motion.div>
                    );
                  }
                  return null;
                }}
              />
              
              <Area
                type="monotone"
                dataKey="value"
                stroke={getMetricColor()}
                strokeWidth={2}
                fill="url(#colorValue)"
                animationDuration={800}
              />
              
              {showBenchmark && metricType === 'benchmark' && (
                <Area
                  type="monotone"
                  dataKey="benchmark"
                  stroke="#6B7280"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  fill="url(#colorBenchmark)"
                  animationDuration={800}
                />
              )}
              
              {/* Scrubbing Line */}
              {scrubbing.isActive && (
                <ReferenceLine
                  x={selectedDataPoint?.date}
                  stroke="#3B82F6"
                  strokeWidth={2}
                  strokeDasharray="2 2"
                />
              )}
            </AreaChart>
          </ResponsiveContainer>

          {/* Scrubbing Indicator */}
          <AnimatePresence>
            {scrubbing.isActive && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                className="absolute top-4 left-4 bg-blue-600 text-white px-3 py-2 rounded-lg text-sm font-medium"
                style={{ left: `${scrubbing.position}%` }}
              >
                Scrubbing: {format(parseISO(scrubbing.timestamp), 'MMM dd')}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Timeline Scrubber */}
        <div className="mt-4 relative">
          <div className="w-full h-2 bg-gray-200 rounded-full">
            <motion.div
              className="h-2 bg-blue-600 rounded-full"
              style={{ width: `${scrubbing.position}%` }}
              animate={{ width: `${scrubbing.position}%` }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>{format(parseISO(timelineData[0]?.date || new Date().toISOString()), 'MMM dd')}</span>
            <span>{format(parseISO(timelineData[timelineData.length - 1]?.date || new Date().toISOString()), 'MMM dd')}</span>
          </div>
        </div>
      </motion.div>

      {/* Performance Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-4"
      >
        {[
          {
            label: 'Period Return',
            value: `${((pie.totalValue - pie.investedAmount) / pie.investedAmount * 100).toFixed(2)}%`,
            color: pie.totalValue >= pie.investedAmount ? 'text-green-600' : 'text-red-600'
          },
          {
            label: 'Best Day',
            value: '+2.34%',
            color: 'text-green-600'
          },
          {
            label: 'Worst Day',
            value: '-1.87%',
            color: 'text-red-600'
          },
          {
            label: 'Volatility',
            value: '15.2%',
            color: 'text-blue-600'
          }
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 + index * 0.1 }}
            className="bg-white/80 backdrop-blur-sm rounded-lg p-4 border border-gray-200"
          >
            <div className={`text-2xl font-bold ${stat.color}`}>
              {stat.value}
            </div>
            <div className="text-sm text-gray-600">{stat.label}</div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
};

export default PiePerformanceTimeline;