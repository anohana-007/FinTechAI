import React from 'react';
import { AnalysisSection } from './AnalysisSection';

const analysisSections = [
  {
    title: '技术分析摘要',
    content: 'MACD金叉形成，RSI指标显示超买信号，建议短期关注回调风险。支撑位在1650元附近。',
    icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 20px; height: 20px; margin-right: 8px"><path d="M7.5 15.8333V10.8333C7.5 10.3913 7.3244 9.96738 7.01184 9.65482C6.69928 9.34226 6.27536 9.16667 5.83333 9.16667H4.16667C4.16667 8.72464 3.99107 8.30072 3.67851 7.98816C3.36595 7.67559 2.94203 7.5 2.5 7.5V12.5C2.5 12.942 2.67559 13.366 2.98816 13.6785C3.30072 13.9911 3.72464 14.1667 4.16667 14.1667H5.83333C6.27536 14.1667 6.69928 13.9911 7.01184 13.6785C7.3244 13.366 7.5 12.942 7.5 12.5V15.8333Z" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>'
  },
  {
    title: '基本面快照',
    content: 'PE比率28.5，ROE 23.2%，净利润同比增长15.8%，基本面表现稳健，估值合理。',
    icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 20px; height: 20px; margin-right: 8px"><path d="M10 6.66668C8.61917 6.66668 7.5 7.41251 7.5 8.33334C7.5 9.25418 8.61917 10 10 10C11.3808 10 12.5 10.7458 12.5 11.6667C12.5 12.5875 11.3808 13.3333 10 13.3333M10 6.66668C10.925 6.66668 11.7333 7.00168 12.1658 7.50001M10 6.66668V5.83334M10 6.66668V13.3333M10 13.3333V14.1667M10 13.3333C9.075 13.3333 8.26667 12.9983 7.83417 12.5" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>'
  },
  {
    title: '市场情绪概览',
    content: '机构持仓比例上升，散户情绪偏向乐观，成交量较前期放大，市场关注度较高。',
    icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 20px; height: 20px; margin-right: 8px"><path d="M5.83333 6.66666H14.1667M5.83333 9.99999H9.16667M10 16.6667L6.66667 13.3333H4.16667C3.72464 13.3333 3.30072 13.1577 2.98816 12.8452C2.67559 12.5326 2.5 12.1087 2.5 11.6667V4.99999C2.5 4.55797 2.67559 4.13404 2.98816 3.82148C3.30072 3.50892 3.72464 3.33333 4.16667 3.33333H15.8333C16.2754 3.33333 16.6993 3.50892 17.0118 3.82148C17.3244 4.13404 17.5 4.55797 17.5 4.99999V11.6667C17.5 12.1087 17.3244 12.5326 17.0118 12.8452C16.6993 13.1577 16.2754 13.3333 15.8333 13.3333H13.3333L10 16.6667Z" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>'
  }
];

export const AnalysisPanel: React.FC = () => {
  return (
    <aside className="p-6 bg-white rounded-xl border border-solid border-neutral-200 h-[722px] w-[296px] max-md:w-full">
      <h2 className="mb-6 text-2xl font-semibold leading-9 text-black">
        AI分析洞察
      </h2>
      <div className="mb-6">
        <h3 className="text-xl font-semibold leading-8 text-black">贵州茅台</h3>
        <p className="text-sm leading-5 text-zinc-500">600519.SH</p>
      </div>
      <div className="flex flex-col items-center mb-6">
        <div className="mb-3 w-24 h-24 text-2xl font-bold leading-9 text-black rounded-full border-4 border-black border-solid bg-neutral-100 flex items-center justify-center">
          85
        </div>
        <p className="text-base leading-6 text-center text-zinc-500">
          AI综合评分
        </p>
      </div>
      <button className="mb-6 w-24 h-10 text-base font-semibold leading-6 text-white bg-green-600 rounded-md">
        买入建议
      </button>
      {analysisSections.map((section, index) => (
        <AnalysisSection key={index} {...section} />
      ))}
    </aside>
  );
};
