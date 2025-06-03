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
  threshold: number;
  threshold_triggered?: number;
  direction: 'UP' | 'DOWN';
  ai_analysis?: AIAnalysisResult | string;
  ai_analysis_summary?: string;
  timestamp?: string;
  is_read?: boolean;
  alert_level?: 'low' | 'medium' | 'high';
  historical_context?: string;
  recommendation?: string;
  user_email?: string;
  message?: string;
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
  
  // AI API Keys配置 (保持向后兼容)
  ai_api_keys?: {
    openai?: string;
    gemini?: string;
    deepseek?: string;
  };
  
  // 新的AI配置结构
  ai_configurations?: {
    [providerId: string]: AIProviderConfig;
  };
  
  // 代理设置
  proxy_settings?: ProxySettings;
  
  // LLM偏好设置
  preferred_llm?: 'openai' | 'gemini' | 'deepseek';
}

export interface AIProviderConfig {
  provider_id: string;
  provider_name: string;
  model_id: string;
  model_name: string;
  base_url: string;
  api_key: string;
  enabled: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface ProxySettings {
  enabled: boolean;
  host: string;
  port: number;
  username?: string;
  password?: string;
  protocol?: 'http' | 'https' | 'socks5';
}

export interface AIProvider {
  id: string;
  name: string;
  description: string;
  default_base_url: string;
  models: AIModel[];
}

export interface AIModel {
  id: string;
  name: string;
  description: string;
}

export interface AIProvidersResponse {
  [providerId: string]: AIProvider;
}

export interface ConnectivityTestRequest {
  provider: string;
  model: string;
  base_url: string;
  api_key: string;
}

export interface ConnectivityTestResponse {
  success: boolean;
  message?: string;
  error?: string;
  provider: string;
  model: string;
  timestamp: string;
  response_data?: any;
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
    ai_keys_detail?: {
      [key: string]: boolean; // 显示哪些LLM已配置API密钥
    };
    ai_configurations_count?: number;
    ai_providers_configured?: string[];
    has_proxy_config?: boolean;
    proxy_enabled?: boolean;
    preferred_llm?: 'openai' | 'gemini' | 'deepseek';
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

// 第二阶段 2.B - AI分析相关类型定义

export interface AIAnalysisResult {
  overall_score: number; // 0-100的评分
  recommendation: 'Buy' | 'Sell' | 'Hold' | 'Monitor'; // 投资建议
  technical_summary: string; // 技术面分析摘要
  fundamental_summary: string; // 基本面分析摘要
  sentiment_summary: string; // 市场情绪分析摘要
  key_reasons: string[]; // 支持推荐决策的关键理由
  confidence_level: 'High' | 'Medium' | 'Low'; // AI分析置信度
  provider?: 'openai' | 'gemini' | 'deepseek'; // 使用的LLM提供商
  error?: boolean; // 是否为错误响应
  message?: string; // 错误消息或其他信息
  raw_response?: string; // 原始响应（备用）
}

export interface ManualAnalysisRequest {
  stock_code: string;
  llm_preference?: 'openai' | 'gemini' | 'deepseek' | 'google';
}

export interface ManualAnalysisResponse {
  success: boolean;
  stock_code: string;
  current_price: number;
  llm_used: 'openai' | 'gemini' | 'deepseek' | 'google';
  analysis: AIAnalysisResult;
  error?: string;
  details?: any;
}

export interface AlertsStatusResponse {
  has_alerts: boolean;
  alerts: AlertInfo[];
}

// LLM提供商配置
export interface LLMProvider {
  id: 'openai' | 'gemini' | 'deepseek' | 'google';
  name: string;
  description: string;
  available: boolean; // 用户是否已配置API密钥
}

// 代理测试相关类型
export interface ProxyTestResult {
  success: boolean;
  error?: string;
  message?: string;
  timestamp: string;
  proxy_config?: {
    host: string;
    port: number;
    protocol: string;
    has_auth: boolean;
  };
  test_results?: Array<{
    test: string;
    success: boolean;
    response_time?: number;
    error?: string;
    data?: any;
  }>;
  summary?: {
    total_tests: number;
    successful_tests: number;
    failed_tests: number;
    average_response_time: number;
  };
}

export interface ProxyValidationResult {
  valid: boolean;
  errors: string[];
}

export interface ProxyTestRequest {
  proxy_settings: ProxySettings;
}

// 更新用户设置响应类型以支持详细信息
export interface UserSettingsDetailResponse {
  success: boolean;
  settings: {
    tushare_token: string;
    email_sender_address: string;
    email_smtp_server: string;
    email_smtp_port: number;
    email_smtp_user: string;
    has_email_password: boolean;
    ai_api_keys: {
      [key: string]: string; // 已掩码的API密钥
    };
    ai_configurations: {
      [providerId: string]: AIProviderConfig;
    };
    proxy_settings: ProxySettings;
    preferred_llm: 'openai' | 'gemini' | 'deepseek';
  };
}

// Tushare Token验证相关类型
export interface TushareTokenValidationResult {
  valid: boolean;
  message: string;
  details: {
    error?: string;
    suggestion?: string;
    test_api?: string;
    sample_count?: number;
    sample_stocks?: Array<{
      ts_code: string;
      symbol: string;
      name: string;
    }>;
  };
}