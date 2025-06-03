import React from 'react';
import { AlertInfo, AIAnalysisResult } from '../types/types';

interface NotificationCardProps {
  onClose: () => void;
  alert?: AlertInfo;
}

export const NotificationCard: React.FC<NotificationCardProps> = ({ onClose, alert: alertInfo }) => {
  // 如果没有传入告警信息，则使用默认值
  const defaultAlert: AlertInfo = {
    id: 1,
    stock_code: '600519.SH',
    stock_name: '贵州茅台',
    current_price: 1685.5,
    threshold: 1700,
    direction: 'UP' as const,
    ai_analysis_summary: '建议减仓'
  };

  const alert = alertInfo || defaultAlert;
  const isAbove = alert.direction === 'UP';

  // 获取AI分析信息
  const getAIAnalysisContent = () => {
    if (alert.ai_analysis) {
      // 如果是结构化的AI分析结果
      if (typeof alert.ai_analysis === 'object') {
        const analysis = alert.ai_analysis as AIAnalysisResult;
        return {
          hasStructuredAnalysis: true,
          score: analysis.overall_score,
          recommendation: analysis.recommendation,
          summary: analysis.technical_summary,
          confidence: analysis.confidence_level,
          provider: analysis.provider
        };
      } else {
        // 兼容旧的文本格式
        return {
          hasStructuredAnalysis: false,
          summary: alert.ai_analysis
        };
      }
    }
    
    // 使用旧的ai_analysis_summary字段作为备用
    if (alert.ai_analysis_summary) {
      return {
        hasStructuredAnalysis: false,
        summary: alert.ai_analysis_summary
      };
    }
    
    return null;
  };

  const aiAnalysis = getAIAnalysisContent();

  // 获取建议的显示样式
  const getRecommendationStyle = (recommendation?: string) => {
    switch (recommendation?.toLowerCase()) {
      case 'buy':
        return { color: 'text-green-600', bg: 'bg-green-100', text: '买入' };
      case 'sell':
        return { color: 'text-red-600', bg: 'bg-red-100', text: '卖出' };
      case 'hold':
        return { color: 'text-blue-600', bg: 'bg-blue-100', text: '持有' };
      case 'monitor':
      default:
        return { color: 'text-gray-600', bg: 'bg-gray-100', text: '观望' };
    }
  };

  // 获取评分颜色
  const getScoreColor = (score?: number) => {
    if (!score) return 'text-gray-600';
    if (score >= 70) return 'text-green-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <aside className="absolute top-4 right-4 p-4 w-96 bg-white rounded-lg border border-solid shadow-lg border-neutral-200 h-auto max-md:right-4 max-md:top-20 max-md:w-80">
      <header className="flex justify-between items-center mb-3">
        <h2 className="text-base font-semibold leading-6 text-black">
          价格{isAbove ? '上破' : '下破'}提醒
        </h2>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
          <div
            dangerouslySetInnerHTML={{
              __html:
                '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M4 12L12 4M4 4L12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
            }}
          />
        </button>
      </header>
      
      <div className="space-y-3">
        {/* 股票基本信息 */}
        <div>
          <h3 className="font-semibold text-gray-900">{alert.stock_name} ({alert.stock_code})</h3>
          <p className="text-sm text-gray-600">
            当前价格: ¥{alert.current_price} | 
            {isAbove ? '突破上限' : '跌破下限'}: ¥{alert.threshold}
          </p>
        </div>

        {/* AI分析信息 */}
        {aiAnalysis && (
          <div className="border-t pt-3">
            {aiAnalysis.hasStructuredAnalysis ? (
              /* 结构化AI分析展示 */
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">AI分析</span>
                  {aiAnalysis.provider && (
                    <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
                      {aiAnalysis.provider.toUpperCase()}
                    </span>
                  )}
                </div>
                
                <div className="flex items-center space-x-4">
                  {/* AI评分 */}
                  {aiAnalysis.score !== undefined && (
                    <div className="text-center">
                      <div className={`text-lg font-bold ${getScoreColor(aiAnalysis.score)}`}>
                        {aiAnalysis.score}
                      </div>
                      <div className="text-xs text-gray-500">评分</div>
                    </div>
                  )}
                  
                  {/* 投资建议 */}
                  {aiAnalysis.recommendation && (
                    <div className="text-center">
                      <div className={`px-2 py-1 rounded text-sm font-medium ${getRecommendationStyle(aiAnalysis.recommendation).color} ${getRecommendationStyle(aiAnalysis.recommendation).bg}`}>
                        {getRecommendationStyle(aiAnalysis.recommendation).text}
                      </div>
                      <div className="text-xs text-gray-500">建议</div>
                    </div>
                  )}
                  
                  {/* 置信度 */}
                  {aiAnalysis.confidence && (
                    <div className="text-center">
                      <div className="text-sm font-medium text-gray-700">
                        {aiAnalysis.confidence === 'High' ? '高' : 
                         aiAnalysis.confidence === 'Medium' ? '中' : '低'}
                      </div>
                      <div className="text-xs text-gray-500">置信度</div>
                    </div>
                  )}
                </div>
                
                {/* 分析摘要 */}
                <p className="text-sm text-gray-700 bg-gray-50 p-2 rounded">
                  {aiAnalysis.summary}
                </p>
              </div>
            ) : (
              /* 简单文本分析展示 */
              <div>
                <span className="text-sm font-medium text-gray-700">AI建议: </span>
                <span className="text-sm text-red-500">{aiAnalysis.summary}</span>
              </div>
            )}
          </div>
        )}

        {/* 时间戳 */}
        {alert.timestamp && (
          <div className="text-xs text-gray-400 border-t pt-2">
            {new Date(alert.timestamp).toLocaleString()}
          </div>
        )}
      </div>
    </aside>
  );
}; 