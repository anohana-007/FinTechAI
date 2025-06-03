import React, { useState, useEffect, useRef, useCallback } from 'react';
import { NewStockData, StockSearchResult } from '../types/types';
import { searchStocksAPI } from '../services/apiService';

interface AddStockFormProps {
  onSubmit: (stockData: NewStockData) => Promise<void>;
  onCancel: () => void;
  userEmail: string;
  isAuthenticated?: boolean;
}

export const AddStockForm: React.FC<AddStockFormProps> = ({ onSubmit, onCancel, userEmail, isAuthenticated = true }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<StockSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);
  const [selectedStock, setSelectedStock] = useState<StockSearchResult | null>(null);
  const [showResults, setShowResults] = useState(false);
  
  const [formData, setFormData] = useState({
    upper_threshold: 0,
    lower_threshold: 0,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const searchRef = useRef<HTMLDivElement>(null);

  const handleSearch = useCallback(async () => {
    if (!searchTerm.trim()) return;

    setIsSearching(true);
    setSearchError(null);
    try {
      const results = await searchStocksAPI(searchTerm, 15);
      setSearchResults(results);
      setShowResults(results.length > 0);
    } catch (error: any) {
      console.error('搜索失败:', error);
      
      // 处理不同类型的错误
      if (error.message && error.message.includes('401')) {
        setSearchError('请先登录后再使用股票搜索功能');
      } else if (error.message && error.message.includes('需要登录')) {
        setSearchError('请先登录后再使用股票搜索功能');
      } else if (error.message && error.message.includes('TUSHARE_TOKEN_MISSING')) {
        setSearchError('请先在用户设置中配置Tushare Token');
      } else if (error.message && error.message.includes('TUSHARE_TOKEN_INVALID')) {
        setSearchError('Tushare Token无效，请检查配置');
      } else {
        setSearchError(error.message || '搜索失败，请重试');
      }
      
      setSearchResults([]);
      setShowResults(false);
    } finally {
      setIsSearching(false);
    }
  }, [searchTerm]);

  // 防抖搜索
  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      if (searchTerm.trim()) {
        handleSearch();
      } else {
        setSearchResults([]);
        setShowResults(false);
        setSearchError(null);
      }
    }, 300);

    return () => clearTimeout(delayDebounce);
  }, [searchTerm, handleSearch]);

  // 点击外部关闭搜索结果
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowResults(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectStock = (stock: StockSearchResult) => {
    setSelectedStock(stock);
    setSearchTerm(`${stock.stock_name} (${stock.stock_code})`);
    setShowResults(false);
    setSearchResults([]);
  };

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: parseFloat(value) || 0
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!selectedStock) {
      setError('请先搜索并选择一支股票');
      return;
    }

    if (!formData.upper_threshold || !formData.lower_threshold) {
      setError('请填写股票的监控阈值');
      return;
    }

    if (formData.upper_threshold <= formData.lower_threshold) {
      setError('上限价格必须大于下限价格');
      return;
    }

    try {
      setIsSubmitting(true);
      const stockData: NewStockData = {
        stock_code: selectedStock.stock_code,
        stock_name: selectedStock.stock_name,
        upper_threshold: formData.upper_threshold,
        lower_threshold: formData.lower_threshold,
        user_email: userEmail
      };
      await onSubmit(stockData);
      onCancel(); // 成功后关闭表单
    } catch (err) {
      setError(err instanceof Error ? err.message : '添加股票失败，请重试');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setSelectedStock(null);
    setSearchTerm('');
    setSearchResults([]);
    setShowResults(false);
    setFormData({ upper_threshold: 0, lower_threshold: 0 });
    setError(null);
    setSearchError(null);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-[500px] max-w-[90vw] max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">添加股票到关注列表</h2>
          <button 
            onClick={onCancel}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-200 text-red-700 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* 股票搜索部分 */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">搜索A股股票</label>
            
            {/* 认证状态提示 */}
            {!isAuthenticated && (
              <div className="mb-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-center">
                  <svg className="h-4 w-4 text-yellow-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <span className="text-sm text-yellow-800">
                    请先登录并配置Tushare Token后再使用股票搜索功能
                  </span>
                </div>
              </div>
            )}
            
            <div className="relative" ref={searchRef}>
              <div className="relative">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onFocus={() => searchResults.length > 0 && setShowResults(true)}
                  placeholder={isAuthenticated ? "输入股票名称或代码进行搜索..." : "请先登录后使用搜索功能"}
                  className={`w-full px-4 py-3 pl-10 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none ${
                    !isAuthenticated ? 'bg-gray-100 cursor-not-allowed' : ''
                  }`}
                  disabled={!isAuthenticated}
                />
                
                {/* 搜索图标 */}
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                
                {/* 加载指示器 */}
                {isSearching && (
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                    <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                  </div>
                )}
              </div>

              {/* 搜索错误 */}
              {searchError && (
                <div className="absolute top-full left-0 right-0 mt-1 p-3 bg-red-50 border border-red-200 rounded-md z-10">
                  <div className="flex items-center">
                    <svg className="h-4 w-4 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    <span className="text-sm text-red-800">{searchError}</span>
                  </div>
                </div>
              )}

              {/* 搜索结果下拉列表 */}
              {showResults && searchResults.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-20 max-h-64 overflow-y-auto">
                  <div className="p-2">
                    <div className="text-xs text-gray-500 mb-2">找到 {searchResults.length} 个结果：</div>
                    {searchResults.map((stock, index) => (
                      <div
                        key={stock.stock_code}
                        onClick={() => handleSelectStock(stock)}
                        className="px-3 py-3 hover:bg-blue-50 cursor-pointer rounded-md border-b border-gray-100 last:border-b-0"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex-1 min-w-0">
                            <div className="font-medium text-gray-900 truncate">
                              {stock.stock_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {stock.stock_code}
                            </div>
                          </div>
                          
                          {/* 匹配类型标签 */}
                          {stock.match_type && (
                            <div className="ml-3 flex-shrink-0">
                              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                                stock.match_type === 'code' 
                                  ? 'bg-blue-100 text-blue-800' 
                                  : 'bg-green-100 text-green-800'
                              }`}>
                                {stock.match_type === 'code' ? '代码' : '名称'}
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* 已选股票显示 */}
          {selectedStock && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-blue-900">已选择股票：</h4>
                  <div className="text-blue-800">
                    <span className="font-semibold">{selectedStock.stock_name}</span>
                    <span className="ml-2 text-sm">({selectedStock.stock_code})</span>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleReset}
                  className="text-blue-600 hover:text-blue-800 text-sm underline"
                >
                  重新选择
                </button>
              </div>
            </div>
          )}

          {/* 阈值设置 */}
          {selectedStock && (
            <div className="mb-6">
              <h4 className="text-sm font-medium mb-3">设置监控阈值</h4>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700">价格上限</label>
                  <input
                    type="number"
                    name="upper_threshold"
                    value={formData.upper_threshold || ''}
                    onChange={handleFormChange}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="触发上限提醒价格"
                    step="0.01"
                    min="0"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1 text-gray-700">价格下限</label>
                  <input
                    type="number"
                    name="lower_threshold"
                    value={formData.lower_threshold || ''}
                    onChange={handleFormChange}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                    placeholder="触发下限提醒价格"
                    step="0.01"
                    min="0"
                    required
                  />
                </div>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                当股价突破设定的上限或下限时，系统将向您发送提醒
              </div>
            </div>
          )}

          {/* 操作按钮 */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !selectedStock}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {isSubmitting ? '添加中...' : '添加到关注列表'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}; 