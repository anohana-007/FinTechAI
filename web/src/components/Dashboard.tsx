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
  const { state } = useAuth();
  
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

  // 如果显示告警日志页面
  if (currentPage === 'alert-log') {
    return <AlertLogPage userEmail={userEmail} onBack={() => setCurrentPage('dashboard')} />;
  }

  return (
    <main className="relative mx-auto max-w-none bg-neutral-100 h-[874px] w-[1271px] max-md:w-full max-md:h-auto max-md:max-w-[991px] max-sm:max-w-screen-sm">
      <Sidebar onNavigate={handleNavigate} currentPage={currentPage} />
      <section className="absolute top-0 left-64 h-[874px] w-[1015px] max-md:relative max-md:left-0 max-md:w-full">
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
            
            {/* 原有的搜索框（用于过滤已添加的股票） */}
            <div className="relative">
              <input
                type="text"
                placeholder="过滤自选股..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="py-2 pr-12 pl-4 w-60 text-base rounded-lg border border-solid border-neutral-200 h-[50px] text-neutral-400 max-sm:w-full"
              />
              <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
                <div
                  dangerouslySetInnerHTML={{
                    __html:
                      '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M17.5 17.5L12.5 12.5M14.1667 8.33333C14.1667 11.555 11.555 14.1667 8.33333 14.1667C5.11167 14.1667 2.5 11.555 2.5 8.33333C2.5 5.11167 5.11167 2.5 8.33333 2.5C11.555 2.5 14.1667 5.11167 14.1667 8.33333Z" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
                  }}
                />
              </div>
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
        
        <div className="flex gap-8 p-8 max-md:flex-col max-md:p-4">
          <section className="p-6 bg-white rounded-xl border border-solid border-neutral-200 h-[722px] w-[623px] max-md:w-full overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold leading-9 text-black">
                我的自选股
              </h2>
              <button 
                className={`py-2 px-4 rounded-lg ${
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
            
            {loading && <p className="text-center py-4">加载中...</p>}
            {error && <p className="text-center py-4 text-red-500">{error}</p>}
            
            {!loading && !error && filteredStocks.length === 0 && (
              <p className="text-center py-4 text-gray-500">
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
          </section>
          
          <section className="w-80 max-md:w-full">
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