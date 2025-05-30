import React from 'react';
import { AlertInfo } from '../types/types';

interface NotificationCardProps {
  onClose: () => void;
  alertInfo?: AlertInfo;
}

export const NotificationCard: React.FC<NotificationCardProps> = ({ onClose, alertInfo }) => {
  // 如果没有传入告警信息，则使用默认值
  const defaultAlert = {
    id: 1,
    stock_code: '600519.SH',
    stock_name: '贵州茅台',
    current_price: 1685.5,
    threshold_triggered: 1700,
    direction: 'UP' as const,
    ai_analysis_summary: '建议减仓'
  };

  const alert = alertInfo || defaultAlert;
  const isAbove = alert.direction === 'UP';

  return (
    <aside className="absolute top-4 right-4 p-4 w-80 bg-white rounded-lg border border-solid shadow-sm border-neutral-200 h-auto max-md:right-4 max-md:top-20">
      <header className="flex justify-between items-center mb-3">
        <h2 className="text-base font-semibold leading-6 text-black">
          价格{isAbove ? '上破' : '下破'}提醒
        </h2>
        <button onClick={onClose}>
          <div
            dangerouslySetInnerHTML={{
              __html:
                '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 12L12 4M4 4L12 12" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
            }}
          />
        </button>
      </header>
      <div>
        <h3>{alert.stock_name} ({alert.stock_code})</h3>
        <p className="mb-2 text-sm leading-5 text-black">
          当前价格: ¥{alert.current_price} | 
          {isAbove ? '突破上限' : '跌破下限'}: ¥{alert.threshold_triggered}
        </p>
        {alert.ai_analysis_summary && (
          <p className="text-sm font-medium leading-5 text-red-500">
            AI建议: {alert.ai_analysis_summary}
          </p>
        )}
      </div>
    </aside>
  );
}; 