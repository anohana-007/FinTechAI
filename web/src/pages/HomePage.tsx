import React, { useState } from 'react';
import Header from '../components/Header';
import { StockCard } from '../components/StockCard';
import { Stock } from '../types/types';
import './HomePage.css';

const HomePage: React.FC = () => {
  const [stocks] = useState<Stock[]>([
    {
      id: 1,
      stock_code: 'SH600000',
      stock_name: '浦发银行',
      current_price: 10.24,
      price_change: '+0.34%',
      upper_threshold: 11.26,
      lower_threshold: 9.22,
      user_email: 'user@example.com'
    },
    {
      id: 2,
      stock_code: 'SZ000001',
      stock_name: '平安银行',
      current_price: 15.78,
      price_change: '-0.42%',
      upper_threshold: 17.36,
      lower_threshold: 14.20,
      user_email: 'user@example.com'
    },
    {
      id: 3,
      stock_code: 'SH601398',
      stock_name: '工商银行',
      current_price: 5.43,
      price_change: '+0.12%',
      upper_threshold: 5.97,
      lower_threshold: 4.89,
      user_email: 'user@example.com'
    }
  ]);

  const handleSelectStock = (stock: Stock) => {
    console.log('Selected stock:', stock);
    // 这里可以添加选择股票后的逻辑，例如显示详情面板
  };

  return (
    <div className="home-page">
      <Header title="股票盯盘应用" />
      <main className="main-content">
        <div className="container">
          <div className="section-header">
            <h2>关注列表</h2>
            <button className="add-stock-btn">添加股票</button>
          </div>
          
          <div className="stock-list">
            {stocks.map(stock => (
              <StockCard
                key={stock.id}
                stock={stock}
                onClick={handleSelectStock}
              />
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default HomePage; 