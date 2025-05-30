export interface StockData {
  name: string;
  code: string;
  price: string;
  change: string;
  upperLimit: string;
  lowerLimit: string;
}

export interface AnalysisSectionData {
  title: string;
  content: string;
  icon: string;
}

export interface NavItemData {
  icon: string;
  label: string;
}

// API类型定义
export interface Stock {
  id?: number;
  stock_code: string;
  stock_name: string;
  current_price?: number;
  price_change?: string;
  upper_threshold: number;
  lower_threshold: number;
  user_email: string;
  last_updated?: string;
  alert_active?: boolean;
  industry?: string;
  created_at?: string;
}

export interface NewStockData {
  stock_code: string;
  stock_name: string;
  upper_threshold: number;
  lower_threshold: number;
  user_email: string;
}

export interface AlertInfo {
  id?: number;
  stock_code: string;
  stock_name: string;
  current_price: number;
  threshold_triggered: number;
  direction: 'UP' | 'DOWN';
  ai_analysis_summary?: string;
  timestamp?: string;
  is_read?: boolean;
  alert_level?: 'low' | 'medium' | 'high';
  historical_context?: string;
  recommendation?: string;
} 