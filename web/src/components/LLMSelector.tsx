import React from 'react';
import { LLMProvider } from '../types/types';

interface LLMSelectorProps {
  availableProviders: LLMProvider[];
  selectedProvider: 'openai' | 'gemini' | 'deepseek' | 'google';
  onProviderChange: (provider: 'openai' | 'gemini' | 'deepseek' | 'google') => void;
  disabled?: boolean;
  className?: string;
}

export const LLMSelector: React.FC<LLMSelectorProps> = ({
  availableProviders,
  selectedProvider,
  onProviderChange,
  disabled = false,
  className = ''
}) => {
  // 过滤出可用的提供商
  const enabledProviders = availableProviders.filter(provider => provider.available);

  if (enabledProviders.length === 0) {
    return (
      <div className={`text-sm text-gray-500 ${className}`}>
        请先在用户设置中配置AI API密钥
      </div>
    );
  }

  return (
    <div className={`flex flex-col space-y-2 ${className}`}>
      <label className="text-sm font-medium text-gray-700">
        选择分析模型
      </label>
      <div className="relative">
        <select
          value={selectedProvider}
          onChange={(e) => onProviderChange(e.target.value as 'openai' | 'gemini' | 'deepseek' | 'google')}
          disabled={disabled}
          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
        >
          {enabledProviders.map((provider) => (
            <option key={provider.id} value={provider.id}>
              {provider.name}
            </option>
          ))}
        </select>
        <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
      <div className="text-xs text-gray-500">
        {enabledProviders.find(p => p.id === selectedProvider)?.description}
      </div>
    </div>
  );
};

// 用于获取LLM提供商列表的工具函数
export const getLLMProviders = (userSettings?: any): LLMProvider[] => {
  // 首先定义基础提供商模板
  const providerTemplates: Record<string, LLMProvider> = {
    'openai': {
      id: 'openai',
      name: 'OpenAI GPT-3.5',
      description: '通用型语言模型，适合综合分析',
      available: false
    },
    'gemini': {
      id: 'gemini',
      name: 'Google Gemini Pro',
      description: 'Google最新模型，多模态能力强',
      available: false
    },
    'google': {
      id: 'google',
      name: 'Google Gemini Pro',
      description: 'Google最新模型，多模态能力强',
      available: false
    },
    'deepseek': {
      id: 'deepseek',
      name: 'DeepSeek V2',
      description: '专业代码和分析模型',
      available: false
    }
  };

  const providers: LLMProvider[] = [];

  // 如果有用户设置，基于实际配置生成提供商列表
  if (userSettings?.ai_configurations) {
    const aiConfigurations = userSettings.ai_configurations;
    
    // 遍历用户的AI配置
    Object.entries(aiConfigurations).forEach(([providerId, config]: [string, any]) => {
      if (config.enabled && config.api_key && providerId in providerTemplates) {
        // 使用实际配置的模型名称
        const provider: LLMProvider = {
          id: providerId as 'openai' | 'gemini' | 'deepseek' | 'google',
          name: config.model_name || providerTemplates[providerId].name,
          description: providerTemplates[providerId].description,
          available: true
        };
        providers.push(provider);
      }
    });
  } 
  // 兼容旧的配置格式
  else if (userSettings?.ai_keys_detail) {
    Object.entries(providerTemplates).forEach(([providerId, template]) => {
      if (providerId in providerTemplates) {
        const provider: LLMProvider = {
          ...template,
          available: !!userSettings.ai_keys_detail[providerId]
        };
        providers.push(provider);
      }
    });
  }

  // 如果没有任何配置，返回默认模板（都不可用）
  if (providers.length === 0) {
    return Object.values(providerTemplates);
  }

  return providers;
}; 