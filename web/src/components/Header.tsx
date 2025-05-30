import React from 'react';
import './Header.css';

interface HeaderProps {
  title: string;
}

const Header: React.FC<HeaderProps> = ({ title }) => {
  return (
    <header className="header">
      <div className="header-container">
        <h1>{title}</h1>
        <nav>
          <ul>
            <li><a href="/">首页</a></li>
            <li><a href="/watchlist">关注列表</a></li>
            <li><a href="/analysis">AI分析</a></li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header; 