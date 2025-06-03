import React, { useState } from 'react';
import { AddStockForm } from './AddStockForm';
import { NewStockData } from '../types/types';

const AddStockDemo: React.FC = () => {
  const [showForm, setShowForm] = useState(false);
  const [mockWatchlist, setMockWatchlist] = useState<NewStockData[]>([]);

  const handleAddStock = async (stockData: NewStockData): Promise<void> => {
    // 模拟添加到关注列表
    setMockWatchlist(prev => [...prev, stockData]);
    console.log('添加股票:', stockData);
    
    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 1000));
  };

  const handleRemoveStock = (index: number) => {
    setMockWatchlist(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h1 className="text-2xl font-bold mb-6">添加股票功能演示</h1>
          
          <div className="mb-6">
            <button
              onClick={() => setShowForm(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              添加股票到关注列表
            </button>
          </div>

          <div className="border-t pt-6">
            <h2 className="text-lg font-semibold mb-4">我的关注列表 ({mockWatchlist.length})</h2>
            
            {mockWatchlist.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>暂无关注股票</p>
                <p className="text-sm">点击上方按钮添加您想关注的股票</p>
              </div>
            ) : (
              <div className="space-y-3">
                {mockWatchlist.map((stock, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">
                        {stock.stock_name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {stock.stock_code}
                      </div>
                      <div className="text-sm text-gray-600 mt-1">
                        监控区间: ¥{stock.lower_threshold} - ¥{stock.upper_threshold}
                      </div>
                    </div>
                    <button
                      onClick={() => handleRemoveStock(index)}
                      className="ml-4 px-3 py-1 text-red-600 hover:text-red-800 border border-red-300 rounded"
                    >
                      移除
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-medium text-blue-900 mb-2">功能说明：</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• 点击"添加股票到关注列表"按钮</li>
            <li>• 在搜索框中输入股票名称或代码（如"平安银行"或"000001"）</li>
            <li>• 系统会实时搜索A股市场并显示匹配结果</li>
            <li>• 点击选择您想关注的股票</li>
            <li>• 设置价格上限和下限阈值</li>
            <li>• 确认添加到关注列表</li>
          </ul>
        </div>
      </div>

      {showForm && (
        <AddStockForm
          onSubmit={handleAddStock}
          onCancel={() => setShowForm(false)}
          userEmail="demo@example.com"
        />
      )}
    </div>
  );
};

export default AddStockDemo; 