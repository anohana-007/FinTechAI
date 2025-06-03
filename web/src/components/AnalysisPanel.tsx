import React, { useState, useEffect } from 'react';
import { AnalysisSection } from './AnalysisSection';
import { LLMSelector, getLLMProviders } from './LLMSelector';
import { AIAnalysisDisplay } from './AIAnalysisDisplay';
import { AlertInfo, Stock, AIAnalysisResult, UserSettingsDetailResponse } from '../types/types';
import { analyzeStockManually, fetchUserSettingsDetail } from '../services/apiService';

interface AnalysisPanelProps {
  selectedStock?: Stock;
  alertInfo?: AlertInfo;
}

export const AnalysisPanel: React.FC<AnalysisPanelProps> = ({ selectedStock, alertInfo }) => {
  const [userSettings, setUserSettings] = useState<UserSettingsDetailResponse | null>(null);
  const [selectedLLM, setSelectedLLM] = useState<'openai' | 'gemini' | 'deepseek' | 'google'>('openai');
  const [analysisResult, setAnalysisResult] = useState<AIAnalysisResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 获取用户设置
  useEffect(() => {
    const loadUserSettings = async () => {
      try {
        const settings = await fetchUserSettingsDetail();
        setUserSettings(settings);
        
        // 获取用户实际配置的LLM提供商
        const llmProviders = getLLMProviders(settings.settings);
        const enabledProviders = llmProviders.filter(provider => provider.available);
        
        // 设置默认LLM选择逻辑
        let defaultLLM: 'openai' | 'gemini' | 'deepseek' | 'google' = 'openai';
        
        if (enabledProviders.length > 0) {
          // 优先使用用户偏好设置（如果该提供商已配置）
          if (settings.settings.preferred_llm && 
              enabledProviders.find(p => p.id === settings.settings.preferred_llm)) {
            defaultLLM = settings.settings.preferred_llm;
          } else {
            // 否则使用第一个可用的提供商
            defaultLLM = enabledProviders[0].id;
          }
        }
        
        setSelectedLLM(defaultLLM);
        
      } catch (error) {
        console.error('Failed to load user settings:', error);
      }
    };

    loadUserSettings();
  }, []);

  // 处理告警信息中的AI分析
  useEffect(() => {
    if (alertInfo?.ai_analysis) {
      // 如果告警包含结构化AI分析
      if (typeof alertInfo.ai_analysis === 'object') {
        setAnalysisResult(alertInfo.ai_analysis);
      } else {
        // 兼容旧的文本格式分析
        setAnalysisResult({
          overall_score: alertInfo.direction === 'UP' ? 75 : 35,
          recommendation: alertInfo.direction === 'UP' ? 'Hold' : 'Monitor',
          technical_summary: alertInfo.ai_analysis,
          fundamental_summary: '基于告警自动生成的分析',
          sentiment_summary: '需要进一步观察市场反应',
          key_reasons: [
            `价格${alertInfo.direction === 'UP' ? '突破上限' : '跌破下限'}: ¥${alertInfo.threshold}`,
            `当前价格: ¥${alertInfo.current_price}`,
            'AI建议关注后续走势'
          ],
          confidence_level: 'Medium'
        });
      }
    }
  }, [alertInfo]);

  // 检查AI配置状态
  const getAIConfigurationStatus = () => {
    if (!userSettings?.settings) {
      return { hasConfigurations: false, enabledCount: 0 };
    }
    
    const aiConfigurations = userSettings.settings.ai_configurations || {};
    const enabledConfigurations = Object.values(aiConfigurations).filter(config => config.enabled);
    
    return {
      hasConfigurations: Object.keys(aiConfigurations).length > 0,
      enabledCount: enabledConfigurations.length,
      totalCount: Object.keys(aiConfigurations).length
    };
  };

  const aiStatus = getAIConfigurationStatus();

  // 直接使用用户设置数据，无需转换
  const llmProviders = getLLMProviders(userSettings?.settings);
  const hasAnyLLMConfigured = llmProviders.some(provider => provider.available);

  // 手动分析股票
  const handleAnalyzeStock = async () => {
    if (!selectedStock) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await analyzeStockManually(selectedStock.stock_code, selectedLLM);
      setAnalysisResult(response.analysis);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'AI分析失败，请稍后重试');
      console.error('Analysis failed:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 当前显示的股票信息
  const currentStock = alertInfo || selectedStock;
  const stockName = currentStock?.stock_name || '请选择股票';
  const stockCode = currentStock?.stock_code || '';
  const currentPrice = alertInfo?.current_price || selectedStock?.current_price;

  // 默认分析内容（当没有AI分析结果时显示）
  const defaultAnalysisSections = [
    {
      title: '技术分析摘要',
      content: '选择股票后点击"获取AI分析"按钮，或等待告警触发以获取AI分析。',
      icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 20px; height: 20px; margin-right: 8px"><path d="M7.5 15.8333V10.8333C7.5 10.3913 7.3244 9.96738 7.01184 9.65482C6.69928 9.34226 6.27536 9.16667 5.83333 9.16667H4.16667C4.16667 8.72464 3.99107 8.30072 3.67851 7.98816C3.36595 7.67559 2.94203 7.5 2.5 7.5V12.5C2.5 12.942 2.67559 13.366 2.98816 13.6785C3.30072 13.9911 3.72464 14.1667 4.16667 14.1667H5.83333C6.27536 14.1667 6.69928 13.9911 7.01184 13.6785C7.3244 13.366 7.5 12.942 7.5 12.5V15.8333Z" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>'
    },
    {
      title: '基本面快照',
      content: '等待分析...',
      icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 20px; height: 20px; margin-right: 8px"><path d="M10 6.66668C8.61917 6.66668 7.5 7.41251 7.5 8.33334C7.5 9.25418 8.61917 10 10 10C11.3808 10 12.5 10.7458 12.5 11.6667C12.5 12.5875 11.3808 13.3333 10 13.3333M10 6.66668C10.925 6.66668 11.7333 7.00168 12.1658 7.50001M10 6.66668V5.83334M10 6.66668V13.3333M10 13.3333V14.1667M10 13.3333C9.075 13.3333 8.26667 12.9983 7.83417 12.5" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>'
    },
    {
      title: '市场情绪概览',
      content: '等待分析...',
      icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 20px; height: 20px; margin-right: 8px"><path d="M5.83333 6.66666H14.1667M5.83333 9.99999H9.16667M10 16.6667L6.66667 13.3333H4.16667C3.72464 13.3333 3.30072 13.1577 2.98816 12.8452C2.67559 12.5326 2.5 12.1087 2.5 11.6667V4.99999C2.5 4.55797 2.67559 4.13404 2.98816 3.82148C3.30072 3.50892 3.72464 3.33333 4.16667 3.33333H15.8333C16.2754 3.33333 16.6993 3.50892 17.0118 3.82148C17.3244 4.13404 17.5 4.55797 17.5 4.99999V11.6667C17.5 12.1087 17.3244 12.5326 17.0118 12.8452C16.6993 13.1577 16.2754 13.3333 15.8333 13.3333H13.3333L10 16.6667Z" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>'
    }
  ];

  return (
    <aside className="p-6 bg-white rounded-xl border border-solid border-neutral-200 h-[722px] w-[296px] max-md:w-full overflow-y-auto">
      <h2 className="mb-6 text-2xl font-semibold leading-9 text-black">
        AI分析洞察
      </h2>
      
      <div className="mb-6">
        <h3 className="text-xl font-semibold leading-8 text-black">{stockName}</h3>
        <p className="text-sm leading-5 text-zinc-500">{stockCode}</p>
        {currentPrice && (
          <p className="text-sm text-gray-600">当前价格: ¥{currentPrice}</p>
        )}
      </div>

      {/* 如果有AI分析结果，显示详细分析 */}
      {analysisResult ? (
        <div className="mb-4">
          <AIAnalysisDisplay
            analysis={analysisResult}
            stockCode={stockCode}
            stockName={stockName}
            currentPrice={currentPrice}
            className="text-sm"
          />
        </div>
      ) : (
        <>
          {/* LLM选择器和分析按钮 */}
          {hasAnyLLMConfigured && selectedStock && (
            <div className="mb-6 space-y-4">
              <LLMSelector
                availableProviders={llmProviders}
                selectedProvider={selectedLLM}
                onProviderChange={setSelectedLLM}
                disabled={isAnalyzing}
                className="text-sm"
              />
              
              <button
                onClick={handleAnalyzeStock}
                disabled={isAnalyzing}
                className={`w-full py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                  isAnalyzing
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {isAnalyzing ? '分析中...' : '获取AI分析'}
              </button>
            </div>
          )}

          {/* 错误信息 */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* 默认AI评分显示 */}
          <div className="flex flex-col items-center mb-6">
            <div className="mb-3 w-24 h-24 text-2xl font-bold leading-9 text-black rounded-full border-4 border-gray-300 border-solid bg-neutral-100 flex items-center justify-center">
              --
            </div>
            <p className="text-base leading-6 text-center text-zinc-500">
              AI综合评分
            </p>
          </div>

          <div className="mb-6 w-24 h-10 text-base font-semibold leading-6 text-white bg-gray-400 rounded-md flex items-center justify-center">
            等待分析
          </div>

          {/* 默认分析部分 */}
          {defaultAnalysisSections.map((section, index) => (
            <AnalysisSection key={index} {...section} />
          ))}

          {/* 智能配置提示 */}
          {!aiStatus.hasConfigurations ? (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
              <p className="text-sm text-yellow-700">
                请先在用户设置中配置AI API密钥以启用AI分析功能。
              </p>
            </div>
          ) : aiStatus.enabledCount === 0 ? (
            <div className="mt-4 p-3 bg-orange-50 border border-orange-200 rounded-md">
              <p className="text-sm text-orange-700">
                已配置AI模型但未启用，请在用户设置中启用至少一个AI配置。
              </p>
            </div>
          ) : (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-md">
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-sm text-green-700">
                  已配置AI模型，可以开始分析。
                </p>
              </div>
              <p className="text-xs text-green-600 mt-1">
                {aiStatus.enabledCount}/{aiStatus.totalCount} 个模型已启用
              </p>
            </div>
          )}
        </>
      )}
    </aside>
  );
}; 