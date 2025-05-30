import React, { useState, useEffect, useRef } from 'react';
import { StockSearchResult, NewStockData } from '../types/types';
import { searchStocks, addStock } from '../services/apiService';

interface StockSearchProps {
  onStockAdded?: () => void;
  userEmail: string;
}

const StockSearch: React.FC<StockSearchProps> = ({ onStockAdded, userEmail }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<StockSearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedStock, setSelectedStock] = useState<StockSearchResult | null>(null);
  const [upperThreshold, setUpperThreshold] = useState('');
  const [lowerThreshold, setLowerThreshold] = useState('');
  const [isAdding, setIsAdding] = useState(false);

  const searchRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      if (searchTerm.trim()) {
        handleSearch();
      } else {
        setSearchResults([]);
        setIsDropdownOpen(false);
      }
    }, 300);

    return () => clearTimeout(delayDebounce);
  }, [searchTerm]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
        setSelectedIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;

    setIsSearching(true);
    try {
      const results = await searchStocks(searchTerm, 10);
      setSearchResults(results);
      setIsDropdownOpen(results.length > 0);
      setSelectedIndex(-1);
    } catch (error) {
      console.error('搜索失败:', error);
      setSearchResults([]);
      setIsDropdownOpen(false);
    } finally {
      setIsSearching(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isDropdownOpen) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => 
          prev < searchResults.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < searchResults.length) {
          handleSelectStock(searchResults[selectedIndex]);
        }
        break;
      case 'Escape':
        setIsDropdownOpen(false);
        setSelectedIndex(-1);
        inputRef.current?.blur();
        break;
    }
  };

  const handleSelectStock = (stock: StockSearchResult) => {
    setSelectedStock(stock);
    setSearchTerm(`${stock.name} (${stock.code})`);
    setIsDropdownOpen(false);
    setShowAddForm(true);
    setUpperThreshold('');
    setLowerThreshold('');
  };

  const handleAddStock = async () => {
    if (!selectedStock || !upperThreshold || !lowerThreshold) {
      alert('请填写完整的阈值信息');
      return;
    }

    const upper = parseFloat(upperThreshold);
    const lower = parseFloat(lowerThreshold);

    if (isNaN(upper) || isNaN(lower)) {
      alert('请输入有效的数字');
      return;
    }

    if (lower >= upper) {
      alert('下限阈值必须小于上限阈值');
      return;
    }

    setIsAdding(true);
    try {
      const stockData: NewStockData = {
        stock_code: selectedStock.code,
        stock_name: selectedStock.name,
        upper_threshold: upper,
        lower_threshold: lower,
        user_email: userEmail,
      };

      await addStock(stockData);
      
      // 重置表单
      setSearchTerm('');
      setSelectedStock(null);
      setShowAddForm(false);
      setUpperThreshold('');
      setLowerThreshold('');
      
      // 通知父组件刷新列表
      if (onStockAdded) {
        onStockAdded();
      }

      alert(`成功添加 ${selectedStock.name} 到关注列表`);
    } catch (error) {
      console.error('添加股票失败:', error);
      alert('添加股票失败，请重试');
    } finally {
      setIsAdding(false);
    }
  };

  const handleCancelAdd = () => {
    setShowAddForm(false);
    setSelectedStock(null);
    setSearchTerm('');
    setUpperThreshold('');
    setLowerThreshold('');
  };

  return (
    <div className="relative" ref={searchRef}>
      {/* 搜索输入框 */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        
        <input
          ref={inputRef}
          type="text"
          className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          placeholder="搜索股票名称或代码..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        
        {isSearching && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          </div>
        )}
      </div>

      {/* 搜索结果下拉列表 */}
      {isDropdownOpen && searchResults.length > 0 && (
        <div className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm">
          {searchResults.map((stock, index) => (
            <div
              key={stock.code}
              className={`cursor-pointer select-none relative py-2 pl-3 pr-9 hover:bg-blue-50 ${
                index === selectedIndex ? 'bg-blue-50 text-blue-900' : 'text-gray-900'
              }`}
              onClick={() => handleSelectStock(stock)}
            >
              <div className="flex items-center">
                <span className="font-medium truncate">{stock.name}</span>
                <span className="ml-2 text-sm text-gray-500">{stock.code}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 添加股票表单弹窗 */}
      {showAddForm && selectedStock && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold mb-4">添加到关注列表</h3>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                股票信息
              </label>
              <div className="text-sm text-gray-600">
                {selectedStock.name} ({selectedStock.code})
              </div>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                上限阈值 *
              </label>
              <input
                type="number"
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                placeholder="请输入上限价格"
                value={upperThreshold}
                onChange={(e) => setUpperThreshold(e.target.value)}
              />
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                下限阈值 *
              </label>
              <input
                type="number"
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                placeholder="请输入下限价格"
                value={lowerThreshold}
                onChange={(e) => setLowerThreshold(e.target.value)}
              />
            </div>

            <div className="flex space-x-3">
              <button
                onClick={handleCancelAdd}
                disabled={isAdding}
                className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50"
              >
                取消
              </button>
              <button
                onClick={handleAddStock}
                disabled={isAdding || !upperThreshold || !lowerThreshold}
                className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isAdding ? '添加中...' : '添加'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockSearch; 