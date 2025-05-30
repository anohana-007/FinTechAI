"use client";
import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { StockCard } from './StockCard';
import { AnalysisPanel } from './AnalysisPanel';
import { NotificationCard } from './NotificationCard';

const stockData = [
  {
    name: '贵州茅台',
    code: '600519.SH',
    price: '¥1685.50',
    change: '+0.14%',
    upperLimit: '¥1700',
    lowerLimit: '¥1650'
  },
  {
    name: '腾讯控股',
    code: '00700.HK',
    price: '¥368.20',
    change: '-1.55%',
    upperLimit: '¥380',
    lowerLimit: '¥350'
  },
  {
    name: '比亚迪',
    code: '002594.SZ',
    price: '¥245.80',
    change: '+3.76%',
    upperLimit: '¥260',
    lowerLimit: '¥230'
  }
];

export const Dashboard: React.FC = () => {
  const [showNotification, setShowNotification] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <main className="relative mx-auto max-w-none bg-neutral-100 h-[874px] w-[1271px] max-md:w-full max-md:h-auto max-md:max-w-[991px] max-sm:max-w-screen-sm">
      <Sidebar />
      <section className="absolute top-0 left-64 h-[874px] w-[1015px] max-md:relative max-md:left-0 max-md:w-full">
        <header className="flex justify-between items-center px-8 py-0 w-full bg-white border-b border-solid border-b-neutral-200 h-[99px] max-sm:flex-col max-sm:gap-4 max-sm:p-4 max-sm:h-auto">
          <h1 className="text-2xl font-semibold leading-9 text-black">
            股票监控仪表盘
          </h1>
          <div className="relative">
            <input
              type="text"
              placeholder="搜索股票代码或名称"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="py-0 pr-12 pl-4 w-80 text-base rounded-lg border border-solid border-neutral-200 h-[50px] text-neutral-400 max-sm:w-full"
            />
            <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
              <div
                dangerouslySetInnerHTML={{
                  __html:
                    '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M17.5 17.5L12.5 12.5M14.1667 8.33333C14.1667 11.555 11.555 14.1667 8.33333 14.1667C5.11167 14.1667 2.5 11.555 2.5 8.33333C2.5 5.11167 5.11167 2.5 8.33333 2.5C11.555 2.5 14.1667 5.11167 14.1667 8.33333Z" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
                }}
              />
            </div>
          </div>
        </header>
        <div className="flex gap-8 p-8 max-md:flex-col max-md:p-4">
          <section className="p-6 bg-white rounded-xl border border-solid border-neutral-200 h-[722px] w-[623px] max-md:w-full">
            <h2 className="mb-6 text-2xl font-semibold leading-9 text-black">
              我的自选股
            </h2>
            {stockData.map((stock, index) => (
              <StockCard key={index} {...stock} />
            ))}
          </section>
          <AnalysisPanel />
        </div>
      </section>
      {showNotification && (
        <NotificationCard onClose={() => setShowNotification(false)} />
      )}
    </main>
  );
};
