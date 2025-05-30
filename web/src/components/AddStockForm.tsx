import React, { useState } from 'react';
import { NewStockData } from '../types/types';

interface AddStockFormProps {
  onSubmit: (stockData: NewStockData) => Promise<void>;
  onCancel: () => void;
  userEmail: string;
}

export const AddStockForm: React.FC<AddStockFormProps> = ({ onSubmit, onCancel, userEmail }) => {
  const [formData, setFormData] = useState<NewStockData>({
    stock_code: '',
    stock_name: '',
    upper_threshold: 0,
    lower_threshold: 0,
    user_email: userEmail
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'upper_threshold' || name === 'lower_threshold' 
        ? parseFloat(value) || 0 
        : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // 简单验证
    if (!formData.stock_code || !formData.stock_name || !formData.user_email) {
      setError('请填写所有必填字段');
      return;
    }

    if (formData.upper_threshold <= formData.lower_threshold) {
      setError('上限价格必须大于下限价格');
      return;
    }

    try {
      setIsSubmitting(true);
      await onSubmit(formData);
      onCancel(); // 成功后关闭表单
    } catch (err) {
      setError(err instanceof Error ? err.message : '添加股票失败，请重试');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-[400px] max-w-full">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">添加股票</h2>
          <button 
            onClick={onCancel}
            className="text-gray-500 hover:text-gray-700"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M4 12L12 4M4 4L12 12" stroke="black" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path>
            </svg>
          </button>
        </div>

        {error && (
          <div className="mb-4 p-2 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">股票代码</label>
            <input
              type="text"
              name="stock_code"
              value={formData.stock_code}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded px-3 py-2"
              placeholder="例如: 600519"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">股票名称</label>
            <input
              type="text"
              name="stock_name"
              value={formData.stock_name}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded px-3 py-2"
              placeholder="例如: 贵州茅台"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-1">价格上限</label>
              <input
                type="number"
                name="upper_threshold"
                value={formData.upper_threshold || ''}
                onChange={handleChange}
                className="w-full border border-gray-300 rounded px-3 py-2"
                placeholder="例如: 1700"
                step="0.01"
                min="0"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">价格下限</label>
              <input
                type="number"
                name="lower_threshold"
                value={formData.lower_threshold || ''}
                onChange={handleChange}
                className="w-full border border-gray-300 rounded px-3 py-2"
                placeholder="例如: 1650"
                step="0.01"
                min="0"
                required
              />
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">接收提醒邮箱</label>
            <input
              type="email"
              name="user_email"
              value={formData.user_email}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded px-3 py-2"
              placeholder="例如: user@example.com"
              required
              disabled
            />
          </div>

          <div className="flex justify-end">
            <button
              type="button"
              onClick={onCancel}
              className="mr-2 px-4 py-2 border border-gray-300 rounded"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-blue-600 text-white rounded disabled:bg-blue-300"
            >
              {isSubmitting ? '添加中...' : '添加股票'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}; 