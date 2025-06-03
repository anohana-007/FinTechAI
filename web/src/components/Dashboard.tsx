import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Sidebar } from './Sidebar';
import { StockCard } from './StockCard';
import { AnalysisPanel } from './AnalysisPanel';
import { NotificationCard } from './NotificationCard';
import { AddStockForm } from './AddStockForm';
import { EditStockForm } from './EditStockForm';
import StockSearch from './StockSearch';
import AlertLogPage from './AlertLogPage';
import { Stock, AlertInfo, NewStockData } from '../types/types';
import { fetchWatchlist, addStock, removeStock, updateStock, checkAlertsStatus } from '../services/apiService';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { state, logout } = useAuth();
  
  // 状态管理
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [editingStock, setEditingStock] = useState<Stock | undefined>(undefined);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStock, setSelectedStock] = useState<Stock | undefined>(undefined);
  const [alertInfo, setAlertInfo] = useState<AlertInfo | undefined>(undefined);
  const [showNotification, setShowNotification] = useState(false);
  const [currentPage, setCurrentPage] = useState<'dashboard' | 'alert-log' | 'settings'>('dashboard');

  // 处理导航
  const handleNavigate = (page: 'dashboard' | 'alert-log' | 'settings') => {
    if (page === 'settings') {
      navigate('/settings');
    } else {
      setCurrentPage(page);
    }
  };

  // 获取用户邮箱（如果用户已登录）
  const userEmail = state.isAuthenticated && state.user ? state.user.email : 'demo@example.com';

  // 加载股票列表
  const loadStocks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchWatchlist();
      setStocks(data);
    } catch (err) {
      console.error('获取股票列表失败:', err);
      if (state.isAuthenticated) {
        setError('获取股票列表失败，请稍后重试');
      } else {
        // 未认证用户显示演示数据
        setStocks([
          {
            stock_code: '600036.SH',
            stock_name: '招商银行',
            current_price: 45.67,
            upper_threshold: 50.0,
            lower_threshold: 40.0,
            user_email: 'demo@example.com',
            alert_active: true
          },
          {
            stock_code: '000001.SZ',
            stock_name: '平安银行',
            current_price: 15.23,
            upper_threshold: 18.0,
            lower_threshold: 12.0,
            user_email: 'demo@example.com',
            alert_active: true
          }
        ]);
      }
    } finally {
      setLoading(false);
    }
  }, [state.isAuthenticated]);

  // 组件加载时获取股票列表
  useEffect(() => {
    loadStocks();
  }, [loadStocks]);

  // 定时检查告警状态（仅对已认证用户）
  useEffect(() => {
    if (!state.isAuthenticated) return;

    const checkAlerts = async () => {
      try {
        const alertResponse = await checkAlertsStatus();
        if (alertResponse.has_alerts && alertResponse.alerts.length > 0) {
          // 显示第一个告警（如果有多个告警，可以在这里实现更复杂的逻辑）
          const firstAlert = alertResponse.alerts[0];
          setAlertInfo(firstAlert);
          setShowNotification(true);
          
          // 如果有告警，选中相关股票
          const alertedStock = stocks.find(s => s.stock_code === firstAlert.stock_code);
          if (alertedStock) {
            setSelectedStock(alertedStock);
          }
        }
      } catch (err) {
        console.error('检查告警状态失败:', err);
      }
    };

    // 立即检查一次
    checkAlerts();

    // 每30秒检查一次
    const intervalId = setInterval(checkAlerts, 30000);
    
    // 清理定时器
    return () => clearInterval(intervalId);
  }, [stocks, state.isAuthenticated]);

  // 处理添加股票
  const handleAddStock = async (newStockData: NewStockData) => {
    try {
      if (!state.isAuthenticated) {
        throw new Error('请先登录后再添加股票');
      }
      await addStock(newStockData);
      loadStocks(); // 重新加载股票列表
      return Promise.resolve();
    } catch (error) {
      return Promise.reject(error);
    }
  };

  // 处理删除股票
  const handleDeleteStock = async (stock: Stock) => {
    try {
      if (!state.isAuthenticated) {
        alert('请先登录后再删除股票');
        return;
      }
      
      // 确认删除
      if (window.confirm(`确定要删除 ${stock.stock_name} (${stock.stock_code}) 吗？`)) {
        await removeStock(stock.stock_code, stock.user_email);
        loadStocks(); // 重新加载股票列表
        
        // 如果删除的是当前选中的股票，清除选中状态
        if (selectedStock && selectedStock.stock_code === stock.stock_code) {
          setSelectedStock(undefined);
        }
      }
    } catch (error) {
      console.error('删除股票失败:', error);
      setError('删除股票失败，请稍后重试');
    }
  };

  // 处理编辑股票
  const handleEditStock = (stock: Stock) => {
    if (!state.isAuthenticated) {
      alert('请先登录后再编辑股票');
      return;
    }
    setEditingStock(stock);
    setShowEditForm(true);
  };

  // 处理更新股票阈值
  const handleUpdateStock = async (stock: Stock, upperThreshold: number, lowerThreshold: number) => {
    try {
      if (!state.isAuthenticated) {
        throw new Error('请先登录后再更新股票');
      }
      
      await updateStock(stock.stock_code, stock.user_email, upperThreshold, lowerThreshold);
      loadStocks(); // 重新加载股票列表
      
      // 如果更新的是当前选中的股票，更新选中状态
      if (selectedStock && selectedStock.stock_code === stock.stock_code) {
        const updatedStock = { ...selectedStock, upper_threshold: upperThreshold, lower_threshold: lowerThreshold };
        setSelectedStock(updatedStock);
      }
    } catch (error) {
      console.error('更新股票阈值失败:', error);
      throw error; // 重新抛出错误以便EditStockForm处理
    }
  };

  // 过滤搜索结果
  const filteredStocks = stocks.filter(stock => 
    stock.stock_code.toLowerCase().includes(searchQuery.toLowerCase()) || 
    stock.stock_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // 移动端导航组件
  const MobileNav = ({ currentPage }: { currentPage: 'dashboard' | 'alert-log' | 'settings' }) => (
    <div className="lg:hidden bg-white border-b border-gray-200 p-4 z-30">
      <div className="flex justify-between items-center">
        <h1 className="text-lg font-semibold text-black">
          FinTech AI
        </h1>
        <div className="flex items-center space-x-4">
          {/* 移动端导航按钮 */}
          <button
            onClick={() => handleNavigate('dashboard')}
            className={`p-2 rounded-lg ${currentPage === 'dashboard' ? 'bg-blue-100 text-blue-600' : 'text-gray-600'}`}
            title="仪表盘"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M7.5 15.8333V10.8333C7.5 10.3913 7.3244 9.96738 7.01184 9.65482C6.69928 9.34226 6.27536 9.16667 5.83333 9.16667H4.16667C3.72464 9.16667 3.30072 9.34226 2.98816 9.65482C2.67559 9.96738 2.5 10.3913 2.5 10.8333V15.8333C2.5 16.2754 2.67559 16.6993 2.98816 17.0118C3.30072 17.3244 3.72464 17.5 4.16667 17.5H5.83333C6.27536 17.5 6.69928 17.3244 7.01184 17.0118C7.3244 16.6993 7.5 16.2754 7.5 15.8333Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          
          {state.isAuthenticated && (
            <>
              <button
                onClick={() => handleNavigate('alert-log')}
                className={`p-2 rounded-lg ${currentPage === 'alert-log' ? 'bg-blue-100 text-blue-600' : 'text-gray-600'}`}
                title="历史告警"
              >
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M10 6.66667V10L12.5 12.5M17.5 10C17.5 14.1421 14.1421 17.5 10 17.5C5.85786 17.5 2.5 14.1421 2.5 10C2.5 5.85786 5.85786 2.5 10 2.5C14.1421 2.5 17.5 5.85786 17.5 10Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
              
              <button
                onClick={() => handleNavigate('settings')}
                className={`p-2 rounded-lg ${currentPage === 'settings' ? 'bg-blue-100 text-blue-600' : 'text-gray-600'}`}
                title="用户设置"
              >
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M8.60417 3.5975C8.95917 2.13417 11.0408 2.13417 11.3958 3.5975M17.5 10C17.5 14.1421 14.1421 17.5 10 17.5C5.85786 17.5 2.5 14.1421 2.5 10C2.5 5.85786 5.85786 2.5 10 2.5C14.1421 2.5 17.5 5.85786 17.5 10Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </button>
            </>
          )}
          
          {/* 移动端登录/登出按钮 */}
          {state.isAuthenticated ? (
            <button
              onClick={() => {
                if (window.confirm('确定要登出吗？')) {
                  logout();
                }
              }}
              className="p-2 rounded-lg text-red-600 hover:bg-red-50"
              title="登出"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M13.3333 14.1667L17.5 10L13.3333 5.83333M17.5 10H7.5M7.5 2.5H5.83333C5.39131 2.5 4.96738 2.67559 4.65482 2.98816C4.34226 3.30072 4.16667 3.72464 4.16667 4.16667V15.8333C4.16667 16.2754 4.34226 16.6993 4.65482 17.0118C4.96738 17.3244 5.39131 17.5 5.83333 17.5H7.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          ) : (
            <button
              onClick={() => navigate('/login')}
              className="p-2 rounded-lg text-indigo-600 hover:bg-indigo-50"
              title="登录"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M6.66667 14.1667L2.5 10L6.66667 5.83333M2.5 10H12.5M12.5 2.5H14.1667C14.6087 2.5 15.0326 2.67559 15.3452 2.98816C15.6577 3.30072 15.8333 3.72464 15.8333 4.16667V15.8333C15.8333 16.2754 15.6577 16.6993 15.3452 17.0118C15.0326 17.3244 14.6087 17.5 14.1667 17.5H12.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );

  // 如果显示告警日志页面
  if (currentPage === 'alert-log') {
    return (
      <main className="relative min-h-screen bg-neutral-100 w-full overflow-hidden">
        <Sidebar onNavigate={handleNavigate} currentPage={currentPage} />
        <MobileNav currentPage={currentPage} />
        <div className="ml-64 max-lg:ml-0">
          <AlertLogPage userEmail={userEmail} onBack={() => setCurrentPage('dashboard')} />
        </div>
      </main>
    );
  }

  return (
    <main className="relative min-h-screen bg-neutral-100 w-full overflow-hidden">
      <Sidebar onNavigate={handleNavigate} currentPage={currentPage} />
      <MobileNav currentPage={currentPage} />
      
      <section className="ml-64 min-h-screen flex flex-col max-lg:ml-0 max-lg:w-full">
        <header className="flex justify-between items-center px-8 py-4 w-full bg-white border-b border-solid border-b-neutral-200 min-h-[99px] max-sm:flex-col max-sm:gap-4 max-sm:p-4">
          <h1 className="text-2xl font-semibold leading-9 text-black">
            股票监控仪表盘 {!state.isAuthenticated && <span className="text-sm text-gray-500">(演示模式)</span>}
          </h1>
          <div className="flex gap-4 items-center max-sm:flex-col max-sm:w-full">
            {/* 股票搜索组件 */}
            <div className="w-80 max-sm:w-full">
              <StockSearch 
                onStockAdded={loadStocks} 
                userEmail={userEmail}
              />
            </div>
          </div>
        </header>

        {/* 未认证用户提示 */}
        {!state.isAuthenticated && (
          <div className="mx-8 mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center">
              <div className="text-blue-600 mr-3">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="currentColor"/>
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-blue-800 font-medium">演示模式</h3>
                <p className="text-blue-700 text-sm">
                  您正在使用演示模式。要使用完整功能，请{' '}
                  <button 
                    onClick={() => navigate('/login')}
                    className="underline hover:no-underline"
                  >
                    登录
                  </button>
                  {' '}或{' '}
                  <button 
                    onClick={() => navigate('/register')}
                    className="underline hover:no-underline"
                  >
                    注册
                  </button>
                  。
                </p>
              </div>
            </div>
          </div>
        )}
        
        <div className="flex-1 flex gap-6 p-6 max-lg:flex-col max-lg:gap-4 max-lg:p-4">
          {/* 股票列表板块 - 优化宽度 */}
          <section className="flex-shrink-0 w-[420px] max-lg:w-full">
            <div className="p-4 bg-white rounded-xl border border-solid border-neutral-200 h-full max-h-[calc(100vh-200px)] overflow-y-auto">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold leading-7 text-black">
                  我的自选股
                </h2>
                <button 
                  className={`py-1.5 px-3 text-sm rounded-lg ${
                    state.isAuthenticated 
                      ? 'bg-blue-600 text-white hover:bg-blue-700' 
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                  onClick={() => state.isAuthenticated ? setShowAddForm(true) : alert('请先登录后再添加股票')}
                  disabled={!state.isAuthenticated}
                >
                  添加股票
                </button>
              </div>
              
              {/* 过滤搜索框移动到这里 */}
              <div className="relative mb-4">
                <input
                  type="text"
                  placeholder="过滤自选股..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="py-2 pr-10 pl-3 w-full text-sm rounded-lg border border-solid border-neutral-200 h-[36px] text-neutral-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <div
                    dangerouslySetInnerHTML={{
                      __html:
                        '<svg width="14" height="14" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M17.5 17.5L12.5 12.5M14.1667 8.33333C14.1667 11.555 11.555 14.1667 8.33333 14.1667C5.11167 14.1667 2.5 11.555 2.5 8.33333C2.5 5.11167 5.11167 2.5 8.33333 2.5C11.555 2.5 14.1667 5.11167 14.1667 8.33333Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
                    }}
                  />
                </div>
              </div>
              
              <div className="space-y-3">
                {loading && <p className="text-center py-4 text-sm text-gray-500">加载中...</p>}
                {error && <p className="text-center py-4 text-red-500 text-sm">{error}</p>}
                
                {!loading && !error && filteredStocks.length === 0 && (
                  <p className="text-center py-4 text-gray-500 text-sm">
                    {searchQuery ? '没有找到匹配的股票' : (
                      state.isAuthenticated 
                        ? '您的自选股列表为空，点击"添加股票"开始'
                        : '演示数据加载中...'
                    )}
                  </p>
                )}
                
                {!loading && !error && filteredStocks.map((stock) => (
                  <StockCard
                    key={stock.stock_code}
                    stock={stock}
                    isSelected={selectedStock?.stock_code === stock.stock_code}
                    onClick={setSelectedStock}
                    onEdit={handleEditStock}
                    onDelete={handleDeleteStock}
                  />
                ))}
              </div>
            </div>
          </section>
          
          {/* AI洞察分析板块 - 扩大为主要区域 */}
          <section className="flex-1 min-w-0">
            <AnalysisPanel selectedStock={selectedStock} />
          </section>
        </div>
        
        {/* 告警通知 */}
        {showNotification && alertInfo && (
          <NotificationCard
            alert={alertInfo}
            onClose={() => setShowNotification(false)}
          />
        )}
        
        {/* 添加股票表单 */}
        {showAddForm && (
          <AddStockForm
            onSubmit={handleAddStock}
            onCancel={() => setShowAddForm(false)}
            userEmail={userEmail}
          />
        )}
        
        {/* 编辑股票表单 */}
        {showEditForm && editingStock && (
          <EditStockForm
            stock={editingStock}
            onSubmit={handleUpdateStock}
            onCancel={() => {
              setShowEditForm(false);
              setEditingStock(undefined);
            }}
          />
        )}
      </section>
    </main>
  );
}; 