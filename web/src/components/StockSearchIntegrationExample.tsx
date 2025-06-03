import React, { useState } from 'react';
import { StockSearchResult, NewStockData } from '../types/types';
import StockSearchBar from './StockSearchBar';
import { addStock } from '../services/apiService';

interface StockSearchIntegrationExampleProps {
  userEmail: string;
  onStockAdded?: () => void;
}

/**
 * 股票搜索集成示例组件
 * 展示如何将 StockSearchBar 集成到实际应用中
 */
const StockSearchIntegrationExample: React.FC<StockSearchIntegrationExampleProps> = ({
  userEmail,
  onStockAdded
}) => {
  const [selectedStock, setSelectedStock] = useState<StockSearchResult | null>(null);
  const [upperThreshold, setUpperThreshold] = useState('');
  const [lowerThreshold, setLowerThreshold] = useState('');
  const [isAdding, setIsAdding] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);

  const handleStockSelect = (stock: StockSearchResult) => {
    setSelectedStock(stock);
    setShowAddForm(true);
    // 重置表单
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
        stock_code: selectedStock.stock_code,
        stock_name: selectedStock.stock_name,
        upper_threshold: upper,
        lower_threshold: lower,
        user_email: userEmail,
      };

      await addStock(stockData);
      
      // 重置表单
      setSelectedStock(null);
      setShowAddForm(false);
      setUpperThreshold('');
      setLowerThreshold('');
      
      // 通知父组件
      if (onStockAdded) {
        onStockAdded();
      }

      alert(`成功添加 ${selectedStock.stock_name} 到关注列表`);
    } catch (error: any) {
      console.error('添加股票失败:', error);
      alert(error.message || '添加股票失败，请重试');
    } finally {
      setIsAdding(false);
    }
  };

  const handleCancelAdd = () => {
    setShowAddForm(false);
    setSelectedStock(null);
    setUpperThreshold('');
    setLowerThreshold('');
  };

  return (
    <div className="space-y-4">
      {/* 使用说明 */}
      <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
        <h3 className="text-lg font-medium text-blue-800 mb-2">
          股票搜索功能演示
        </h3>
        <p className="text-sm text-blue-700">
          在下方搜索框中输入股票名称或代码，选择股票后可以添加到关注列表中。
        </p>
      </div>

      {/* 股票搜索栏 */}
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          搜索股票
        </label>
        <StockSearchBar
          onStockSelect={handleStockSelect}
          placeholder="输入股票名称或代码进行搜索..."
          className="w-full max-w-md"
        />
      </div>

      {/* 选中的股票信息 */}
      {selectedStock && (
        <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
          <h4 className="text-sm font-medium text-gray-800 mb-2">已选择股票：</h4>
          <div className="flex items-center space-x-4">
            <div>
              <span className="font-medium text-gray-900">{selectedStock.stock_name}</span>
              <span className="ml-2 text-sm text-gray-500">({selectedStock.stock_code})</span>
            </div>
            {selectedStock.match_type && (
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                selectedStock.match_type === 'code' 
                  ? 'bg-blue-100 text-blue-800' 
                  : 'bg-green-100 text-green-800'
              }`}>
                {selectedStock.match_type === 'code' ? '代码匹配' : '名称匹配'}
              </span>
            )}
          </div>
        </div>
      )}

      {/* 添加股票表单 */}
      {showAddForm && selectedStock && (
        <div className="border border-gray-200 rounded-md p-4 bg-white">
          <h3 className="text-lg font-semibold mb-4">设置监控阈值</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                上限阈值 *
              </label>
              <input
                type="number"
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="请输入上限价格"
                value={upperThreshold}
                onChange={(e) => setUpperThreshold(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                下限阈值 *
              </label>
              <input
                type="number"
                step="0.01"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="请输入下限价格"
                value={lowerThreshold}
                onChange={(e) => setLowerThreshold(e.target.value)}
              />
            </div>
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
              {isAdding ? '添加中...' : '添加到关注列表'}
            </button>
          </div>
        </div>
      )}

      {/* API 调用示例代码 */}
      <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
        <h4 className="text-sm font-medium text-gray-800 mb-2">API 调用示例：</h4>
        <pre className="text-xs text-gray-600 bg-white p-3 rounded border overflow-x-auto">
{`// 1. 导入API函数
import { searchStocksAPI } from '../services/apiService';

// 2. 调用搜索API
const searchResults = await searchStocksAPI('平安', 10);

// 3. 处理搜索结果
searchResults.forEach(stock => {
  console.log(\`\${stock.stock_name} (\${stock.stock_code})\`);
});`}
        </pre>
      </div>
    </div>
  );
};

export default StockSearchIntegrationExample; 