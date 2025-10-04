// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

// Authentication Types
export interface AuthState {
  isAuthenticated: boolean;
  apiKey?: string;
  connectionStatus: 'connected' | 'disconnected' | 'connecting' | 'error';
  lastConnected?: Date;
}

// Portfolio Types
export interface Portfolio {
  id: string;
  totalValue: number;
  totalInvested: number;
  totalReturn: number;
  totalReturnPercentage: number;
  pies: Pie[];
  lastUpdated: Date;
}

export interface Pie {
  id: string;
  name: string;
  totalValue: number;
  investedAmount: number;
  returnAmount: number;
  returnPercentage: number;
  positions: Position[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Position {
  symbol: string;
  name: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  marketValue: number;
  unrealizedPnl: number;
  sector?: string;
  industry?: string;
  country?: string;
  assetType: 'STOCK' | 'ETF' | 'CRYPTO';
}

// Metrics Types
export interface PortfolioMetrics {
  totalValue: number;
  totalInvested: number;
  totalReturn: number;
  annualizedReturn: number;
  volatility: number;
  sharpeRatio: number;
  maxDrawdown: number;
  beta: number;
}

export interface PieMetrics {
  pieId: string;
  totalValue: number;
  returnPercentage: number;
  contributionToPortfolio: number;
  volatility: number;
  sharpeRatio: number;
  riskCategory: 'LOW' | 'MEDIUM' | 'HIGH';
}

// API Error Types
export interface ApiError {
  message: string;
  code?: string;
  status?: number;
  details?: any;
}