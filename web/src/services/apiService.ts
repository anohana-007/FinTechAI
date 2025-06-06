import { 
  Stock, 
  NewStockData, 
  AlertInfo, 
  StockSearchResult, 
  StockSearchResponse, 
  AlertLogEntry, 
  AlertLogResponse, 
  PaginationParams,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  SessionResponse,
  UserSettingsData,
  UserSettingsResponse,
  UserSettingsDetailResponse,
  ChangePasswordRequest,
  AIAnalysisResult,
  ManualAnalysisRequest,
  ManualAnalysisResponse,
  AlertsStatusResponse,
  AIProvidersResponse,
  ConnectivityTestRequest,
  ConnectivityTestResponse,
  ProxyTestRequest,
  ProxyTestResult,
  ProxyValidationResult,
  TushareTokenValidationResult
} from '../types/types';

const API_BASE_URL = 'http://localhost:5000';

const makeRequest = async (url: string, options: RequestInit = {}): Promise<Response> => {
  const defaultOptions: RequestInit = {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };
  return fetch(url, defaultOptions);
};

export const fetchWatchlist = async (): Promise<Stock[]> => {
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/watchlist`);
    if (!response.ok) {
      throw new Error(`Failed to fetch watchlist: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    return data as Stock[];
  } catch (error) {
    console.error('Error fetching watchlist:', error);
    throw error;
  }
};

export const addStock = async (stockData: NewStockData): Promise<any> => {
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/add_stock`, {
      method: 'POST',
      body: JSON.stringify(stockData),
    });
    if (!response.ok) {
      throw new Error(`Failed to add stock: ${response.status} ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error adding stock:', error);
    throw error;
  }
};

export const removeStock = async (stockCode: string, userEmail: string): Promise<any> => {
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/remove_stock`, {
      method: 'DELETE',
      body: JSON.stringify({
        stock_code: stockCode,
        user_email: userEmail,
      }),
    });
    if (!response.ok) {
      throw new Error(`Failed to remove stock: ${response.status} ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error removing stock:', error);
    throw error;
  }
};

export const updateStock = async (
  stockCode: string, 
  userEmail: string, 
  upperThreshold: number, 
  lowerThreshold: number
): Promise<any> => {
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/update_stock`, {
      method: 'PUT',
      body: JSON.stringify({
        stock_code: stockCode,
        user_email: userEmail,
        upper_threshold: upperThreshold,
        lower_threshold: lowerThreshold,
      }),
    });
    if (!response.ok) {
      throw new Error(`Failed to update stock: ${response.status} ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error updating stock:', error);
    throw error;
  }
};

export const checkAlertsStatus = async (): Promise<AlertsStatusResponse> => {
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/check_alerts_status`);
    if (!response.ok) {
      throw new Error(`Failed to check alerts: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    return data as AlertsStatusResponse;
  } catch (error) {
    console.error('Error checking alerts:', error);
    throw error;
  }
};

export const searchStocksAPI = async (searchTerm: string, limit: number = 20): Promise<StockSearchResult[]> => {
  try {
    if (!searchTerm.trim()) {
      return [];
    }
    const params = new URLSearchParams({
      query: searchTerm.trim(),
      limit: limit.toString(),
    });
    const response = await makeRequest(`${API_BASE_URL}/api/stock_search?${params}`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || errorData.message || `Stock search failed: ${response.status}`);
    }
    const data: StockSearchResponse = await response.json();
    return data.results;
  } catch (error) {
    console.error('Error searching stocks:', error);
    throw error;
  }
};

// 保持向后兼容性的别名
export const searchStocks = searchStocksAPI;

export const fetchAlertLog = async (params: PaginationParams = {}): Promise<AlertLogResponse> => {
  try {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params.user_email) queryParams.append('user_email', params.user_email);
    if (params.stock_code) queryParams.append('stock_code', params.stock_code);
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);

    const response = await makeRequest(`${API_BASE_URL}/api/alert_log?${queryParams}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch alert log: ${response.status} ${response.statusText}`);
    }
    const data: AlertLogResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching alert log:', error);
    throw error;
  }
};

export const fetchStockPrice = async (stockCode: string): Promise<{ code: string; price: number }> => {
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/stock_price/${stockCode}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch stock price: ${response.status} ${response.statusText}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching stock price:', error);
    throw error;
  }
};

export const login = async (credentials: LoginRequest): Promise<AuthResponse> => {
  try {
    console.log('发送登录请求到:', `${API_BASE_URL}/auth/login`);
    
    const response = await makeRequest(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      console.log('登录失败，错误信息:', errorData);
      throw new Error(errorData.error || `Login failed: ${response.status}`);
    }
    const data: AuthResponse = await response.json();
    console.log('登录成功');
    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

export const register = async (userData: RegisterRequest): Promise<AuthResponse> => {
  try {
    const response = await makeRequest(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Registration failed: ${response.status}`);
    }
    const data: AuthResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
};

export const logout = async (): Promise<void> => {
  try {
    const response = await makeRequest(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Logout failed: ${response.status} ${response.statusText}`);
    }
  } catch (error) {
    console.error('Logout error:', error);
    throw error;
  }
};

export const checkSession = async (): Promise<SessionResponse> => {
  try {
    console.log('checkSession: 开始检查会话状态');
    const response = await makeRequest(`${API_BASE_URL}/auth/check_session`);
    console.log('checkSession: 收到响应，状态码:', response.status);
    console.log('checkSession: 响应头:', Object.fromEntries(response.headers.entries()));
    
    if (!response.ok) {
      console.log('checkSession: 响应不正常，状态码:', response.status);
      // 如果是401，表示未认证，这是正常情况
      if (response.status === 401) {
        return { authenticated: false };
      }
      throw new Error(`Session check failed: ${response.status} ${response.statusText}`);
    }
    const data: SessionResponse = await response.json();
    console.log('checkSession: 成功获取会话数据:', data);
    return data;
  } catch (error) {
    console.error('checkSession: 检查会话时发生错误:', error);
    // 网络错误时，返回未认证状态而不是抛出错误
    return { authenticated: false };
  }
};

export const fetchUserSettings = async (): Promise<UserSettingsResponse> => {
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/user/settings`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Failed to fetch user settings: ${response.status}`);
    }
    const data: UserSettingsResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching user settings:', error);
    throw error;
  }
};

export const fetchUserSettingsDetail = async (): Promise<UserSettingsDetailResponse> => {
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/user/settings?detail=true`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Failed to fetch user settings detail: ${response.status}`);
    }
    const data: UserSettingsDetailResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching user settings detail:', error);
    throw error;
  }
};

export const updateUserSettings = async (settings: UserSettingsData): Promise<AuthResponse> => {
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/user/settings`, {
      method: 'POST',
      body: JSON.stringify(settings),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Failed to update user settings: ${response.status}`);
    }
    const data: AuthResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error updating user settings:', error);
    throw error;
  }
};

export const changePassword = async (passwordData: ChangePasswordRequest): Promise<AuthResponse> => {
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/user/password`, {
      method: 'PUT',
      body: JSON.stringify(passwordData),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Failed to change password: ${response.status}`);
    }
    const data: AuthResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error changing password:', error);
    throw error;
  }
};

export const analyzeStockManually = async (
  stockCode: string, 
  llmPreference?: 'openai' | 'gemini' | 'deepseek' | 'google'
): Promise<ManualAnalysisResponse> => {
  try {
    const requestData: ManualAnalysisRequest = {
      stock_code: stockCode
    };
    
    if (llmPreference) {
      requestData.llm_preference = llmPreference;
    }

    const response = await makeRequest(`${API_BASE_URL}/api/analyze_stock_manually`, {
      method: 'POST',
      body: JSON.stringify(requestData),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Analysis failed: ${response.status} ${response.statusText}`);
    }
    
    const data: ManualAnalysisResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error analyzing stock manually:', error);
    throw error;
  }
};

export const fetchAIProviders = async (): Promise<AIProvidersResponse> => {
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/ai_providers`);
    if (!response.ok) {
      throw new Error(`Failed to fetch AI providers: ${response.status} ${response.statusText}`);
    }
    const data: AIProvidersResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching AI providers:', error);
    throw error;
  }
};

export const testAIConnectivity = async (
  testData: ConnectivityTestRequest
): Promise<ConnectivityTestResponse> => {
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/test_ai_connectivity`, {
      method: 'POST',
      body: JSON.stringify(testData),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Connectivity test failed: ${response.status} ${response.statusText}`);
    }
    
    const data: ConnectivityTestResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Error testing AI connectivity:', error);
    throw error;
  }
};

export const testProxyConnectivity = async (
  proxySettings: ProxyTestRequest['proxy_settings']
): Promise<ProxyTestResult> => {
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/test_proxy_connectivity`, {
      method: 'POST',
      body: JSON.stringify({ proxy_settings: proxySettings }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Proxy test failed: ${response.status} ${response.statusText}`);
    }
    
    const data: ProxyTestResult = await response.json();
    return data;
  } catch (error) {
    console.error('Error testing proxy connectivity:', error);
    throw error;
  }
};

export const validateProxySettings = async (
  proxySettings: ProxyTestRequest['proxy_settings']
): Promise<ProxyValidationResult> => {
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/validate_proxy_settings`, {
      method: 'POST',
      body: JSON.stringify({ proxy_settings: proxySettings }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `Proxy validation failed: ${response.status} ${response.statusText}`);
    }
    
    const data: ProxyValidationResult = await response.json();
    return data;
  } catch (error) {
    console.error('Error validating proxy settings:', error);
    throw error;
  }
};

export const validateTushareToken = async (token: string): Promise<TushareTokenValidationResult> => {
  try {
    const response = await makeRequest(`${API_BASE_URL}/api/validate_tushare_token`, {
      method: 'POST',
      body: JSON.stringify({ token }),
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || `Token validation failed: ${response.status} ${response.statusText}`);
    }
    
    const data: TushareTokenValidationResult = await response.json();
    return data;
  } catch (error) {
    console.error('Error validating Tushare token:', error);
    throw error;
  }
};
