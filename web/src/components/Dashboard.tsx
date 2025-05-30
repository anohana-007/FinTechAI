import React, { useState, useEffect, useCallback } from 'react';
import { Sidebar } from './Sidebar';
import { StockCard } from './StockCard';
import { AnalysisPanel } from './AnalysisPanel';
import { NotificationCard } from './NotificationCard';
import { AddStockForm } from './AddStockForm';
import { Stock, AlertInfo, NewStockData } from '../types/types';
import { fetchWatchlist, addStock, checkAlertsStatus } from '../services/apiService';

export const Dashboard: React.FC = () => {
  // 状态管理
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStock, setSelectedStock] = useState<Stock | undefined>(undefined);
  const [alertInfo, setAlertInfo] = useState<AlertInfo | undefined>(undefined);
  const [showNotification, setShowNotification] = useState(false);

  // 加载股票列表
  const loadStocks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchWatchlist();
      setStocks(data);
    } catch (err) {
      console.error('获取股票列表失败:', err);
      setError('获取股票列表失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  }, []);

  // 组件加载时获取股票列表
  useEffect(() => {
    loadStocks();
  }, [loadStocks]);

  // 定时检查告警状态
  useEffect(() => {
    const checkAlerts = async () => {
      try {
        const alertData = await checkAlertsStatus();
        if (alertData) {
          setAlertInfo(alertData);
          setShowNotification(true);
          // 如果有告警，选中相关股票
          const alertedStock = stocks.find(s => s.stock_code === alertData.stock_code);
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
  }, [stocks]);

  // 处理添加股票
  const handleAddStock = async (newStockData: NewStockData) => {
    try {
      await addStock(newStockData);
      loadStocks(); // 重新加载股票列表
      return Promise.resolve();
    } catch (error) {
      return Promise.reject(error);
    }
  };

  // 过滤搜索结果
  const filteredStocks = stocks.filter(stock => 
    stock.stock_code.toLowerCase().includes(searchQuery.toLowerCase()) || 
    stock.stock_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <main className="relative mx-auto max-w-none bg-neutral-100 h-[874px] w-[1271px] max-md:w-full max-md:h-auto max-md:max-w-[991px] max-sm:max-w-screen-sm">
      <Sidebar />
      <section className="absolute top-0 left-64 h-[874px] w-[1015px] max-md:relative max-md:left-0 max-md:w-full">
        <header className="flex justify-between items-center px-8 py-0 w-full bg-white border-b border-solid border-b-neutral-200 h-[99px] max-sm:flex-col max-sm:gap-4 max-sm:p-4 max-sm:h-auto">
          <h1 className="text-2xl font-semibold leading-9 text-black">
            股票监控仪表盘
          </h1>
          <div className="relative">
            <input
              type="text"
              placeholder="搜索股票代码或名称"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="py-0 pr-12 pl-4 w-80 text-base rounded-lg border border-solid border-neutral-200 h-[50px] text-neutral-400 max-sm:w-full"
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
        </header>
        <div className="flex gap-8 p-8 max-md:flex-col max-md:p-4">
          <section className="p-6 bg-white rounded-xl border border-solid border-neutral-200 h-[722px] w-[623px] max-md:w-full overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold leading-9 text-black">
                我的自选股
              </h2>
              <button 
                className="bg-blue-600 text-white py-2 px-4 rounded-lg"
                onClick={() => setShowAddForm(true)}
              >
                添加股票
              </button>
            </div>
            
            {loading && <p className="text-center py-4">加载中...</p>}
            {error && <p className="text-center py-4 text-red-500">{error}</p>}
            
            {!loading && !error && filteredStocks.length === 0 && (
              <p className="text-center py-4 text-gray-500">
                {searchQuery ? '没有找到匹配的股票' : '您的自选股列表为空，点击"添加股票"开始'}
              </p>
            )}
            
            {filteredStocks.map((stock) => (
              <StockCard 
                key={stock.stock_code} 
                stock={stock} 
                onSelect={setSelectedStock}
              />
            ))}
          </section>
          <AnalysisPanel selectedStock={selectedStock} alertInfo={alertInfo} />
        </div>
      </section>
      
      {showNotification && alertInfo && (
        <NotificationCard 
          onClose={() => setShowNotification(false)} 
          alertInfo={alertInfo}
        />
      )}
      
      {showAddForm && (
        <AddStockForm 
          onAddStock={handleAddStock} 
          onClose={() => setShowAddForm(false)} 
        />
      )}
    </main>
  );
}; 