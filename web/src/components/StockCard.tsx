import React from 'react';
import './StockCard.css';
import { Stock } from '../types/types';

interface StockCardProps {
  stock: Stock;
  isSelected?: boolean;
  onClick: (stock: Stock) => void;
  onDelete?: (stock: Stock) => void;
  onEdit?: (stock: Stock) => void;
}

export const StockCard: React.FC<StockCardProps> = ({ stock, isSelected, onClick, onDelete, onEdit }) => {
  const { stock_name, stock_code, current_price, upper_threshold, lower_threshold } = stock;
  
  // 格式化显示的值
  const formattedPrice = current_price ? `¥${current_price.toFixed(2)}` : '加载中...';
  const formattedUpperThreshold = `¥${upper_threshold.toFixed(2)}`;
  const formattedLowerThreshold = `¥${lower_threshold.toFixed(2)}`;
  
  // 简单的涨跌状态显示，如果没有价格则显示中性
  const priceChangeStatus = !current_price ? 'neutral' : 
    current_price > upper_threshold ? 'positive' :
    current_price < lower_threshold ? 'negative' : 'neutral';
  
  return (
    <article 
      className={`relative p-3 rounded-lg border border-solid bg-neutral-100 border-neutral-200 w-full min-h-[120px] hover:shadow-md transition-shadow cursor-pointer ${
        isSelected ? 'ring-2 ring-blue-500 bg-blue-50' : ''
      }`}
      onClick={() => onClick(stock)}
    >
      {/* 股票基本信息 */}
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1 min-w-0 pr-3">
          <h3 className="text-base font-semibold leading-5 text-black truncate">{stock_name}</h3>
          <p className="text-xs leading-4 text-zinc-500 mt-1">{stock_code}</p>
        </div>
        <div className="text-right flex-shrink-0">
          <p className={`text-lg font-semibold leading-5 ${
            priceChangeStatus === 'positive' ? 'text-red-500' : 
            priceChangeStatus === 'negative' ? 'text-green-500' : 'text-black'
          }`}>
            {formattedPrice}
          </p>
          {stock.price_change && (
            <p className="text-xs font-medium leading-4 mt-1">
              {stock.price_change}
            </p>
          )}
        </div>
      </div>
      
      {/* 价格阈值信息 */}
      <div className="mb-2">
        <p className="text-xs text-zinc-500 mb-1">价格提醒</p>
        <div className="flex flex-wrap gap-1 text-xs">
          <span className="bg-red-50 px-2 py-0.5 rounded text-red-700 text-xs">
            上限: {formattedUpperThreshold}
          </span>
          <span className="bg-green-50 px-2 py-0.5 rounded text-green-700 text-xs">
            下限: {formattedLowerThreshold}
          </span>
        </div>
      </div>
      
      {/* 操作按钮 */}
      <div className="flex gap-1.5 justify-end">
        {onEdit && (
          <button 
            className="text-xs font-medium text-white bg-blue-500 hover:bg-blue-600 rounded px-2 py-1 transition-colors"
            onClick={(e) => {
              e.stopPropagation();
              onEdit(stock);
            }}
            title="编辑阈值"
          >
            编辑
          </button>
        )}
        {onDelete && (
          <button 
            className="text-xs font-medium text-white bg-red-500 hover:bg-red-600 rounded px-2 py-1 transition-colors"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(stock);
            }}
            title="删除股票"
          >
            删除
          </button>
        )}
      </div>
    </article>
  );
}; 