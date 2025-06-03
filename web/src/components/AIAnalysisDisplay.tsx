import React, { useState } from 'react';
import { AIAnalysisResult } from '../types/types';

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
  const [activeTab, setActiveTab] = useState<'technical' | 'fundamental' | 'sentiment'>('technical');

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

  return (
    <div className={`bg-white rounded-xl border border-neutral-200 ${className}`}>
      {/* 头部信息 */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-semibold text-black">{stockName}</h3>
            <p className="text-sm text-gray-500">{stockCode}</p>
            {currentPrice && (
              <p className="text-sm text-gray-600">当前价格: ¥{currentPrice}</p>
            )}
          </div>
          {analysis.provider && (
            <div className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
              由 {analysis.provider.toUpperCase()} 分析
            </div>
          )}
        </div>

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

        {/* 分析选项卡 */}
        <div className="mb-4">
          <div className="flex space-x-4 border-b border-gray-200">
            <button
              onClick={() => setActiveTab('technical')}
              className={`py-2 px-4 text-sm font-medium border-b-2 ${
                activeTab === 'technical'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              技术分析
            </button>
            <button
              onClick={() => setActiveTab('fundamental')}
              className={`py-2 px-4 text-sm font-medium border-b-2 ${
                activeTab === 'fundamental'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              基本面
            </button>
            <button
              onClick={() => setActiveTab('sentiment')}
              className={`py-2 px-4 text-sm font-medium border-b-2 ${
                activeTab === 'sentiment'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              市场情绪
            </button>
          </div>
        </div>

        {/* 选项卡内容 */}
        <div className="min-h-[120px]">
          {activeTab === 'technical' && (
            <div className="space-y-2">
              <h5 className="font-medium text-gray-900 flex items-center">
                <svg className="w-4 h-4 mr-2 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3 3a1 1 0 000 2v8a2 2 0 002 2h2.586l-1.293 1.293a1 1 0 101.414 1.414L10 15.414l2.293 2.293a1 1 0 001.414-1.414L12.414 15H15a2 2 0 002-2V5a1 1 0 100-2H3zm11.707 4.707a1 1 0 00-1.414-1.414L10 9.586 8.707 8.293a1 1 0 00-1.414 0l-2 2a1 1 0 101.414 1.414L8 10.414l1.293 1.293a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                技术面分析
              </h5>
              <p className="text-sm text-gray-700 leading-relaxed">{analysis.technical_summary}</p>
            </div>
          )}

          {activeTab === 'fundamental' && (
            <div className="space-y-2">
              <h5 className="font-medium text-gray-900 flex items-center">
                <svg className="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M4 4a2 2 0 00-2 2v1h16V6a2 2 0 00-2-2H4zM18 9H2v5a2 2 0 002 2h12a2 2 0 002-2V9zM4 13a1 1 0 011-1h1a1 1 0 110 2H5a1 1 0 01-1-1zm5-1a1 1 0 100 2h1a1 1 0 100-2H9z" />
                </svg>
                基本面分析
              </h5>
              <p className="text-sm text-gray-700 leading-relaxed">{analysis.fundamental_summary}</p>
            </div>
          )}

          {activeTab === 'sentiment' && (
            <div className="space-y-2">
              <h5 className="font-medium text-gray-900 flex items-center">
                <svg className="w-4 h-4 mr-2 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                市场情绪分析
              </h5>
              <p className="text-sm text-gray-700 leading-relaxed">{analysis.sentiment_summary}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}; 