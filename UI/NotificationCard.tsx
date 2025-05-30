import React from 'react';

interface NotificationCardProps {
  onClose: () => void;
}

export const NotificationCard: React.FC<NotificationCardProps> = ({ onClose }) => {
  return (
    <aside className="absolute top-4 right-4 p-4 w-80 bg-white rounded-lg border border-solid shadow-sm border-neutral-200 h-[149px] max-md:right-4 max-md:top-20">
      <header className="flex justify-between items-center mb-3">
        <h2 className="text-base font-semibold leading-6 text-black">
          价格突破提醒
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
        <h3>贵州茅台 (600519.SH)</h3>
        <p className="mb-2 text-sm leading-5 text-black">
          当前价格: ¥1685.50 | 突破上限: ¥1700
        </p>
        <p className="text-sm font-medium leading-5 text-red-500">
          AI建议: 建议减仓
        </p>
      </div>
    </aside>
  );
};
