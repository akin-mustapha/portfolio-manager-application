import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  AnimatedTimeSeriesChart,
  InteractiveLineChart,
  AnimatedScatterChart,
  TimeSeriesDataPoint,
  LineChartDataPoint,
  LineConfig,
  ScatterDataPoint
} from '../components/charts';

// Mock data generators for demonstration
const generateTimeSeriesData = (): TimeSeriesDataPoint[] => {
  const data: TimeSeriesDataPoint[] = [];
  const startDate = new Date('2023-01-01');
  let value = 10000;
  
  for (let i = 0; i < 365; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    
    // Simulate portfolio growth with some volatility
    const dailyReturn = (Math.random() - 0.48) * 0.02; // Slight positive bias
    value *= (1 + dailyReturn);
    
    data.push({
      date: date.toISOString().split('T')[0],
      value: value,
      label: `Portfolio value: £${value.toLocaleString()}`
    });
  }
  
  return data;
};

const generateBenchmarkData = (): LineChartDataPoint[] => {
  const data: LineChartDataPoint[] = [];
  const startDate = new Date('2023-01-01');
  let portfolioValue = 0;
  let sp500Value = 0;
  let ftse100Value = 0;
  
  for (let i = 0; i < 365; i++) {
    const date = new Date(startDate);
    date.setDate(date.getDate() + i);
    
    // Simulate different performance patterns
    portfolioValue += (Math.random() - 0.47) * 0.3; // Slightly better than market
    sp500Value += (Math.random() - 0.48) * 0.25;
    ftse100Value += (Math.random() - 0.49) * 0.2;
    
    data.push({
      date: date.toISOString().split('T')[0],
      portfolio: portfolioValue,
      sp500: sp500Value,
      ftse100: ftse100Value
    });
  }
  
  return data;
};

const generateRiskReturnData = (): ScatterDataPoint[] => {
  const pies = [
    'Tech Growth', 'Dividend Aristocrats', 'Emerging Markets', 'Real Estate',
    'Healthcare', 'Energy', 'Consumer Goods', 'Financial Services'
  ];
  
  return pies.map((pie, index) => ({
    x: Math.random() * 25 + 5, // Risk (volatility) 5-30%
    y: Math.random() * 20 - 5, // Return -5% to 15%
    size: Math.random() * 8 + 6, // Size 6-14
    label: pie,
    category: index < 4 ? 'Growth' : 'Value',
    color: index < 4 ? '#3B82F6' : '#10B981',
    metadata: {
      'Market Value': `£${(Math.random() * 50000 + 10000).toLocaleString()}`,
      'Holdings': Math.floor(Math.random() * 20 + 5),
      'Sharpe Ratio': (Math.random() * 2).toFixed(2)
    }
  }));
};

const PerformanceAnalysis: React.FC = () => {
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesDataPoint[]>([]);
  const [benchmarkData, setBenchmarkData] = useState<LineChartDataPoint[]>([]);
  const [riskReturnData, setRiskReturnData] = useState<ScatterDataPoint[]>([]);
  const [loading, setLoading] = useState(true);

  const benchmarkLines: LineConfig[] = [
    {
      key: 'portfolio',
      name: 'Your Portfolio',
      color: '#3B82F6',
      strokeWidth: 3,
      visible: true
    },
    {
      key: 'sp500',
      name: 'S&P 500',
      color: '#10B981',
      strokeWidth: 2,
      strokeDasharray: '5,5',
      visible: true
    },
    {
      key: 'ftse100',
      name: 'FTSE 100',
      color: '#F59E0B',
      strokeWidth: 2,
      strokeDasharray: '3,3',
      visible: true
    }
  ];

  useEffect(() => {
    // Simulate data loading
    const loadData = async () => {
      setLoading(true);
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setTimeSeriesData(generateTimeSeriesData());
      setBenchmarkData(generateBenchmarkData());
      setRiskReturnData(generateRiskReturnData());
      setLoading(false);
    };
    
    loadData();
  }, []);

  const handlePointClick = (point: any) => {
    console.log('Point clicked:', point);
    // Handle point click - could open modal, navigate, etc.
  };

  const handleLineToggle = (lineKey: string, visible: boolean) => {
    console.log(`Line ${lineKey} toggled to ${visible ? 'visible' : 'hidden'}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Performance Analysis
          </h1>
          <p className="text-gray-600">
            Interactive charts for portfolio performance and risk analysis
          </p>
        </motion.div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {/* Time Series Chart */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="xl:col-span-2"
          >
            <AnimatedTimeSeriesChart
              data={timeSeriesData}
              loading={loading}
              height={350}
              title="Portfolio Value Over Time"
              yAxisLabel="Portfolio Value (£)"
              color="#3B82F6"
              formatValue={(value) => `£${value.toLocaleString()}`}
              onPointClick={handlePointClick}
              className="shadow-lg"
            />
          </motion.div>

          {/* Benchmark Comparison */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="xl:col-span-2"
          >
            <InteractiveLineChart
              data={benchmarkData}
              lines={benchmarkLines}
              loading={loading}
              height={400}
              title="Benchmark Comparison"
              yAxisLabel="Cumulative Return (%)"
              showBrush={true}
              showLegend={true}
              formatValue={(value) => `${value.toFixed(1)}%`}
              onLineToggle={handleLineToggle}
              onDataPointClick={handlePointClick}
              className="shadow-lg"
            />
          </motion.div>

          {/* Risk-Return Scatter Plot */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="xl:col-span-2"
          >
            <AnimatedScatterChart
              data={riskReturnData}
              loading={loading}
              height={450}
              title="Risk vs Return Analysis"
              xAxisLabel="Risk (Volatility %)"
              yAxisLabel="Return (%)"
              enableZoom={true}
              enablePan={true}
              onPointClick={handlePointClick}
              onPointHover={(point) => console.log('Hovered:', point?.label)}
              className="shadow-lg"
            />
          </motion.div>
        </div>

        {/* Chart Controls */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white/50 backdrop-blur-sm rounded-lg border border-gray-200 p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Chart Interactions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Time Series Chart</h4>
              <ul className="space-y-1">
                <li>• Hover over points for details</li>
                <li>• Click points for more info</li>
                <li>• Smooth data transitions</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Benchmark Chart</h4>
              <ul className="space-y-1">
                <li>• Toggle lines in legend</li>
                <li>• Use brush to zoom time range</li>
                <li>• Interactive tooltips</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Scatter Plot</h4>
              <ul className="space-y-1">
                <li>• Scroll to zoom in/out</li>
                <li>• Drag to pan around</li>
                <li>• Click reset to center</li>
              </ul>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default PerformanceAnalysis;