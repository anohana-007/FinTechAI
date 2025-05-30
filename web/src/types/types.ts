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

// 第二阶段新增类型定义

export interface StockSearchResult {
  code: string;
  name: string;
}

export interface StockSearchResponse {
  query: string;
  count: number;
  results: StockSearchResult[];
}

export interface AlertLogEntry {
  id: number;
  user_id?: string;
  stock_code: string;
  stock_name: string;
  alert_timestamp: string;
  triggered_price: number;
  threshold_price: number;
  direction: 'UP' | 'DOWN';
  ai_analysis?: string;
  user_email?: string;
  created_at: string;
  updated_at: string;
}

export interface AlertLogResponse {
  success: boolean;
  data: AlertLogEntry[];
  pagination: {
    page: number;
    page_size: number;
    total_count: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
  user_email?: string;
  stock_code?: string;
  start_date?: string;
  end_date?: string;
}

// 用户认证相关类型定义

export interface User {
  id: number;
  username: string;
  email: string;
  created_at?: string;
  updated_at?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  message: string;
  user?: User;
}

export interface SessionResponse {
  authenticated: boolean;
  user?: User;
}

// 用户设置相关类型定义

export interface UserSettingsData {
  // Tushare配置
  tushare_token?: string;
  
  // 邮件配置
  email_sender_address?: string;
  email_smtp_server?: string;
  email_smtp_port?: number;
  email_smtp_user?: string;
  email_smtp_password?: string; // 仅用于提交，不用于显示
  
  // AI API Keys配置
  ai_api_keys?: {
    openai?: string;
    gemini?: string;
    deepseek?: string;
  };
}

export interface UserSettingsResponse {
  success: boolean;
  settings: {
    has_tushare_token: boolean;
    has_email_config: boolean;
    email_sender_address?: string;
    email_smtp_server?: string;
    email_smtp_port?: number;
    email_smtp_user?: string;
    has_email_password: boolean;
    ai_keys_count: number;
  };
}

// 认证上下文状态
export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  loading: boolean;
}

// 修改密码请求
export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
}