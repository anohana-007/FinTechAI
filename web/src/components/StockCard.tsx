import React from 'react';
import './StockCard.css';
import { Stock } from '../types/types';

interface StockCardProps {
  stock: Stock;
  onSelect: (stock: Stock) => void;
}

export const StockCard: React.FC<StockCardProps> = ({ stock, onSelect }) => {
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
      className="relative px-4 py-5 mb-4 rounded-lg border border-solid bg-neutral-100 border-neutral-200 h-[167px] w-[573px] hover:shadow-md transition-shadow cursor-pointer"
      onClick={() => onSelect(stock)}
    >
      <div className="absolute left-[17px] top-[19px]">
        <h3 className="mb-2 text-lg font-semibold leading-7 text-black">{stock_name}</h3>
        <p className="mb-3.5 text-sm leading-5 text-zinc-500">{stock_code}</p>
        <p className="text-sm leading-5 text-zinc-500">价格提醒</p>
      </div>
      <div className="absolute text-right right-[17px] top-[17px]">
        <p className={`mb-px text-xl font-semibold leading-8 ${
          priceChangeStatus === 'positive' ? 'text-red-500' : 
          priceChangeStatus === 'negative' ? 'text-green-500' : 'text-black'
        }`}>
          {formattedPrice}
        </p>
        <p className="mb-3.5 text-sm font-medium leading-5">
          {stock.price_change || '-'}
        </p>
        <p className="text-sm leading-5 text-zinc-500">
          <span className="mr-2">上限: {formattedUpperThreshold}</span>
          <span>| 下限: {formattedLowerThreshold}</span>
        </p>
      </div>
      <button 
        className="absolute text-sm font-medium leading-5 text-white bg-black rounded-md cursor-pointer bottom-[17px] h-[37px] right-[17px] w-[101px]"
        onClick={(e) => {
          e.stopPropagation();
          onSelect(stock);
        }}
      >
        查看AI分析
      </button>
    </article>
  );
}; 