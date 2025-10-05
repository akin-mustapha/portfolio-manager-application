// Core data types for the application

export interface Portfolio {
  id: string;
  totalValue: number;
  totalInvested: number;
  totalReturn: number;
  returnPercentage: number;
  pies: Pie[];
  lastUpdated: string;
}

export interface Pie {
  id: string;
  name: string;
  totalValue: number;
  investedAmount: number;
  returnPct: number;
  positions?: Position[];
  createdAt: string;
  updatedAt: string;
}

export interface Position {
  symbol: string;
  name: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  marketValue: number;
  unrealizedPnl: number;
  sector: string;
  industry: string;
  country: string;
  assetType: AssetType;
}

export enum AssetType {
  STOCK = 'STOCK',
  ETF = 'ETF',
  CRYPTO = 'CRYPTO'
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface ConnectionStatus {
  connected: boolean;
  lastSync?: string;
  error?: string;
}