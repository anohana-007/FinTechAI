import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { User, AuthState } from '../types/types';
import { checkSession, logout as logoutApi } from '../services/apiService';

// 定义行动类型
type AuthAction = 
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'LOGIN_SUCCESS'; payload: User }
  | { type: 'LOGOUT_SUCCESS' }
  | { type: 'SET_AUTHENTICATED'; payload: { user: User; authenticated: boolean } };

// 初始状态
const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  loading: true,
};

// Reducer函数
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload,
      };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload,
        loading: false,
      };
    case 'LOGOUT_SUCCESS':
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        loading: false,
      };
    case 'SET_AUTHENTICATED':
      return {
        ...state,
        isAuthenticated: action.payload.authenticated,
        user: action.payload.user,
        loading: false,
      };
    default:
      return state;
  }
};

// 上下文接口
interface AuthContextType {
  state: AuthState;
  login: (user: User) => void;
  logout: () => Promise<void>;
  checkAuthStatus: () => Promise<void>;
}

// 创建上下文
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// AuthProvider组件
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // 登录成功后更新状态
  const login = (user: User) => {
    dispatch({ type: 'LOGIN_SUCCESS', payload: user });
  };

  // 登出
  const logout = async () => {
    try {
      await logoutApi();
    } catch (error) {
      console.error('登出时出错:', error);
      // 即使API调用失败，也要清除本地状态
    } finally {
      dispatch({ type: 'LOGOUT_SUCCESS' });
    }
  };

  // 检查认证状态
  const checkAuthStatus = async () => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      const sessionData = await checkSession();
      
      if (sessionData.authenticated && sessionData.user) {
        dispatch({ 
          type: 'SET_AUTHENTICATED', 
          payload: { 
            user: sessionData.user, 
            authenticated: true 
          } 
        });
      } else {
        dispatch({ 
          type: 'SET_AUTHENTICATED', 
          payload: { 
            user: {} as User, 
            authenticated: false 
          } 
        });
      }
    } catch (error) {
      console.error('检查认证状态时出错:', error);
      dispatch({ 
        type: 'SET_AUTHENTICATED', 
        payload: { 
          user: {} as User, 
          authenticated: false 
        } 
      });
    }
  };

  // 应用启动时检查认证状态
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const value: AuthContextType = {
    state,
    login,
    logout,
    checkAuthStatus,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// 自定义Hook
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth必须在AuthProvider内使用');
  }
  return context;
};

export default AuthContext; 