import React, { useState, useCallback } from 'react';
import { StockSearchResult } from '../types/types';
import { searchStocksAPI } from '../services/apiService';

interface StockSearchBarProps {
  onStockSelect?: (stock: StockSearchResult) => void;
  placeholder?: string;
  className?: string;
}

/**
 * 简化的股票搜索栏组件
 * 用于演示如何使用 searchStocksAPI 函数
 */
const StockSearchBar: React.FC<StockSearchBarProps> = ({
  onStockSelect,
  placeholder = "搜索股票名称或代码...",
  className = ""
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<StockSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showDropdown, setShowDropdown] = useState(false);

  // 防抖搜索函数
  const debounceSearch = useCallback(
    (term: string) => {
      const timeoutId = setTimeout(async () => {
        if (!term.trim()) {
          setResults([]);
          setShowDropdown(false);
          setError(null);
          return;
        }

        setIsLoading(true);
        setError(null);
        
        try {
          const searchResults = await searchStocksAPI(term, 10);
          setResults(searchResults);
          setShowDropdown(searchResults.length > 0);
        } catch (err: any) {
          console.error('股票搜索失败:', err);
          setError(err.message || '搜索失败，请重试');
          setResults([]);
          setShowDropdown(false);
        } finally {
          setIsLoading(false);
        }
      }, 300);

      return () => clearTimeout(timeoutId);
    },
    []
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchTerm(value);
    
    // 清理之前的定时器并启动新的搜索
    const cleanup = debounceSearch(value);
    return cleanup;
  };

  const handleStockSelect = (stock: StockSearchResult) => {
    setSearchTerm(`${stock.stock_name} (${stock.stock_code})`);
    setShowDropdown(false);
    setResults([]);
    
    if (onStockSelect) {
      onStockSelect(stock);
    }
  };

  const handleInputBlur = () => {
    // 延迟隐藏下拉列表，以便用户能够点击结果项
    setTimeout(() => {
      setShowDropdown(false);
    }, 200);
  };

  return (
    <div className={`relative ${className}`}>
      {/* 搜索输入框 */}
      <div className="relative">
        <input
          type="text"
          value={searchTerm}
          onChange={handleInputChange}
          onBlur={handleInputBlur}
          onFocus={() => results.length > 0 && setShowDropdown(true)}
          placeholder={placeholder}
          className="w-full px-4 py-2 pl-10 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
        />
        
        {/* 搜索图标 */}
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        
        {/* 加载指示器 */}
        {isLoading && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          </div>
        )}
      </div>

      {/* 错误消息 */}
      {error && (
        <div className="absolute top-full left-0 right-0 mt-1 p-3 bg-red-50 border border-red-200 rounded-md z-10">
          <div className="flex items-center">
            <svg className="h-4 w-4 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span className="text-sm text-red-800">{error}</span>
          </div>
        </div>
      )}

      {/* 搜索结果下拉列表 */}
      {showDropdown && results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-md shadow-lg z-20 max-h-60 overflow-y-auto">
          {results.map((stock, index) => (
            <div
              key={stock.stock_code}
              onClick={() => handleStockSelect(stock)}
              className="px-4 py-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
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
                      {stock.match_type === 'code' ? '代码匹配' : '名称匹配'}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default StockSearchBar; 