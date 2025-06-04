import React, { useState } from 'react';
import { AIAnalysisResult } from '../types/types';
import { DetailModal } from './DetailModal';

interface AIAnalysisDisplayProps {
  analysis: AIAnalysisResult;
  stockCode: string;
  stockName: string;
  currentPrice?: number;
  className?: string;
}

export const AIAnalysisDisplay: React.FC<AIAnalysisDisplayProps> = ({
  analysis,
  stockCode,
  stockName,
  currentPrice,
  className = ''
}) => {
  const [modalState, setModalState] = useState<{
    isOpen: boolean;
    title: string;
    content: string;
    icon: string;
  }>({
    isOpen: false,
    title: '',
    content: '',
    icon: ''
  });

  // 获取评分颜色
  const getScoreColor = (score: number) => {
    if (score >= 70) return 'text-green-600 border-green-500';
    if (score >= 40) return 'text-yellow-600 border-yellow-500';
    return 'text-red-600 border-red-500';
  };

  // 获取建议颜色和图标
  const getRecommendationStyle = (recommendation: string) => {
    switch (recommendation.toLowerCase()) {
      case 'buy':
        return { color: 'bg-green-600', icon: '↗', text: '买入' };
      case 'sell':
        return { color: 'bg-red-600', icon: '↘', text: '卖出' };
      case 'hold':
        return { color: 'bg-blue-600', icon: '=', text: '持有' };
      case 'monitor':
      default:
        return { color: 'bg-gray-600', icon: '👁', text: '观望' };
    }
  };

  // 获取置信度颜色
  const getConfidenceColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'high':
        return 'text-green-600 bg-green-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'low':
      default:
        return 'text-red-600 bg-red-100';
    }
  };

  const recommendationStyle = getRecommendationStyle(analysis.recommendation);

  // 打开详细报告模态框
  const openDetailModal = (type: 'technical' | 'fundamental' | 'sentiment') => {
    const modalConfigs = {
      technical: {
        title: '技术分析详细报告',
        content: analysis.technical_summary,
        icon: '📈'
      },
      fundamental: {
        title: '基本面分析详细报告',
        content: analysis.fundamental_summary,
        icon: '💰'
      },
      sentiment: {
        title: '市场情绪分析详细报告',
        content: analysis.sentiment_summary,
        icon: '🎯'
      }
    };

    const config = modalConfigs[type];
    setModalState({
      isOpen: true,
      ...config
    });
  };

  // 关闭模态框
  const closeModal = () => {
    setModalState(prev => ({ ...prev, isOpen: false }));
  };

  // 截取摘要文本（显示前100个字符）
  const getTruncatedText = (text: string, maxLength: number = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  // 如果是错误响应，显示错误信息
  if (analysis.error) {
    return (
      <div className={`p-4 border border-red-200 rounded-lg bg-red-50 ${className}`}>
        <div className="flex items-center space-x-2 mb-2">
          <div className="w-6 h-6 text-red-500">⚠️</div>
          <h3 className="text-lg font-semibold text-red-700">AI分析暂不可用</h3>
        </div>
        <p className="text-red-600">{analysis.message || '分析服务遇到问题，请稍后重试'}</p>
      </div>
    );
  }

  // 分析模块数据
  const analysisModules = [
    {
      id: 'technical',
      title: '技术分析摘要',
      content: getTruncatedText(analysis.technical_summary),
      fullContent: analysis.technical_summary,
      icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 20px; height: 20px; margin-right: 8px"><path d="M7.5 15.8333V10.8333C7.5 10.3913 7.3244 9.96738 7.01184 9.65482C6.69928 9.34226 6.27536 9.16667 5.83333 9.16667H4.16667C4.16667 8.72464 3.99107 8.30072 3.67851 7.98816C3.36595 7.67559 2.94203 7.5 2.5 7.5V12.5C2.5 12.942 2.67559 13.366 2.98816 13.6785C3.30072 13.9911 3.72464 14.1667 4.16667 14.1667H5.83333C6.27536 14.1667 6.69928 13.9911 7.01184 13.6785C7.3244 13.366 7.5 12.942 7.5 12.5V15.8333Z" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>'
    },
    {
      id: 'fundamental',
      title: '基本面快照',
      content: getTruncatedText(analysis.fundamental_summary),
      fullContent: analysis.fundamental_summary,
      icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 20px; height: 20px; margin-right: 8px"><path d="M10 6.66668C8.61917 6.66668 7.5 7.41251 7.5 8.33334C7.5 9.25418 8.61917 10 10 10C11.3808 10 12.5 10.7458 12.5 11.6667C12.5 12.5875 11.3808 13.3333 10 13.3333M10 6.66668C10.925 6.66668 11.7333 7.00168 12.1658 7.50001M10 6.66668V5.83334M10 6.66668V13.3333M10 13.3333V14.1667M10 13.3333C9.075 13.3333 8.26667 12.9983 7.83417 12.5" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>'
    },
    {
      id: 'sentiment',
      title: '市场情绪概览',
      content: getTruncatedText(analysis.sentiment_summary),
      fullContent: analysis.sentiment_summary,
      icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 20px; height: 20px; margin-right: 8px"><path d="M5.83333 6.66666H14.1667M5.83333 9.99999H9.16667M10 16.6667L6.66667 13.3333H4.16667C3.72464 13.3333 3.30072 13.1577 2.98816 12.8452C2.67559 12.5326 2.5 12.1087 2.5 11.6667V4.99999C2.5 4.55797 2.67559 4.13404 2.98816 3.82148C3.30072 3.50892 3.72464 3.33333 4.16667 3.33333H15.8333C16.2754 3.33333 16.6993 3.50892 17.0118 3.82148C17.3244 4.13404 17.5 4.55797 17.5 4.99999V11.6667C17.5 12.1087 17.3244 12.5326 17.0118 12.8452C16.6993 13.1577 16.2754 13.3333 15.8333 13.3333H13.3333L10 16.6667Z" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>'
    }
  ];

  return (
    <div className={`bg-white rounded-xl border border-neutral-200 ${className}`}>
      {/* 头部信息 */}
      <div className="p-6 border-b border-gray-200">
        {/* 评分和建议 */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {/* AI综合评分 */}
            <div className="flex flex-col items-center">
              <div className={`w-16 h-16 rounded-full border-4 flex items-center justify-center text-xl font-bold ${getScoreColor(analysis.overall_score)}`}>
                {analysis.overall_score}
              </div>
              <p className="text-xs text-gray-500 mt-1">AI评分</p>
            </div>

            {/* 投资建议 */}
            <div className="flex flex-col items-center">
              <button className={`w-20 h-10 text-sm font-semibold text-white rounded-md ${recommendationStyle.color} flex items-center justify-center space-x-1`}>
                <span>{recommendationStyle.icon}</span>
                <span>{recommendationStyle.text}</span>
              </button>
              <p className="text-xs text-gray-500 mt-1">建议</p>
            </div>

            {/* 置信度 */}
            <div className="flex flex-col items-center">
              <div className={`px-3 py-2 rounded-md text-sm font-medium ${getConfidenceColor(analysis.confidence_level)}`}>
                {analysis.confidence_level === 'High' ? '高' : 
                 analysis.confidence_level === 'Medium' ? '中' : '低'}
              </div>
              <p className="text-xs text-gray-500 mt-1">置信度</p>
            </div>
          </div>
        </div>
      </div>

      {/* 分析详情 */}
      <div className="p-6">
        {/* 关键理由 */}
        <div className="mb-6">
          <h4 className="text-lg font-semibold text-black mb-3">关键理由</h4>
          <ul className="space-y-2">
            {analysis.key_reasons.map((reason, index) => (
              <li key={index} className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                <span className="text-sm text-gray-700">{reason}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* 分析模块网格 - 与第一张图保持一致的卡片风格 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-3">
          {analysisModules.map((module) => (
            <div key={module.id} className="p-3 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-start space-x-2 mb-3">
                <div 
                  className="flex-shrink-0 mt-0.5"
                  dangerouslySetInnerHTML={{ __html: module.icon }}
                />
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-semibold text-gray-900 mb-1">
                    {module.title}
                  </h4>
                </div>
              </div>
              <p className="text-gray-600 text-xs leading-relaxed mb-3">
                {module.content}
              </p>
              <button
                onClick={() => openDetailModal(module.id as 'technical' | 'fundamental' | 'sentiment')}
                className="w-full px-3 py-2 text-xs font-medium text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-md transition-colors border border-blue-200"
              >
                详细报告
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 详细报告模态框 */}
      <DetailModal
        isOpen={modalState.isOpen}
        onClose={closeModal}
        title={modalState.title}
        content={modalState.content}
        icon={modalState.icon}
      />
    </div>
  );
}; 