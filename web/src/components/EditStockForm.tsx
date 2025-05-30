import React, { useState } from 'react';
import { Stock } from '../types/types';

interface EditStockFormProps {
  stock: Stock;
  onSubmit: (stock: Stock, upperThreshold: number, lowerThreshold: number) => Promise<void>;
  onCancel: () => void;
}

export const EditStockForm: React.FC<EditStockFormProps> = ({ stock, onSubmit, onCancel }) => {
  const [upperThreshold, setUpperThreshold] = useState<string>(stock.upper_threshold.toString());
  const [lowerThreshold, setLowerThreshold] = useState<string>(stock.lower_threshold.toString());
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // 验证输入
      const upperValue = parseFloat(upperThreshold);
      const lowerValue = parseFloat(lowerThreshold);

      if (isNaN(upperValue) || isNaN(lowerValue)) {
        setError('请输入有效的数字');
        return;
      }

      if (lowerValue >= upperValue) {
        setError('下限阈值必须小于上限阈值');
        return;
      }

      if (upperValue <= 0 || lowerValue <= 0) {
        setError('阈值必须大于0');
        return;
      }

      // 调用更新函数
      await onSubmit(stock, upperValue, lowerValue);
      onCancel();
    } catch (err: any) {
      setError(err.message || '更新失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-[400px] max-w-full">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">编辑阈值设置</h2>
          <button 
            onClick={onCancel}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 12L12 4M4 4L12 12" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path>
            </svg>
          </button>
        </div>

        <div className="mb-4 p-3 bg-gray-50 rounded">
          <h3 className="font-medium text-gray-900">{stock.stock_name}</h3>
          <p className="text-sm text-gray-500">{stock.stock_code}</p>
          {stock.current_price && (
            <p className="text-sm text-gray-600">当前价格: ¥{stock.current_price.toFixed(2)}</p>
          )}
        </div>

        {error && (
          <div className="mb-4 p-2 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              上限阈值 (¥)
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={upperThreshold}
              onChange={(e) => setUpperThreshold(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              placeholder="输入上限阈值"
              required
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              下限阈值 (¥)
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={lowerThreshold}
              onChange={(e) => setLowerThreshold(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              placeholder="输入下限阈值"
              required
            />
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onCancel}
              className="flex-1 py-2 px-4 text-gray-700 bg-gray-200 rounded-lg hover:bg-gray-300 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-2 px-4 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {loading ? '更新中...' : '更新阈值'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}; 