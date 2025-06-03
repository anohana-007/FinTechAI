import React, { useState, useEffect } from 'react';
import { 
  AIProvider, 
  AIProviderConfig, 
  AIProvidersResponse, 
  ConnectivityTestResponse 
} from '../types/types';
import { fetchAIProviders, testAIConnectivity } from '../services/apiService';

interface AIConfigurationPanelProps {
  configurations: { [providerId: string]: AIProviderConfig };
  onConfigurationChange: (configs: { [providerId: string]: AIProviderConfig }) => void;
  className?: string;
}

export const AIConfigurationPanel: React.FC<AIConfigurationPanelProps> = ({
  configurations,
  onConfigurationChange,
  className = ''
}) => {
  const [providers, setProviders] = useState<AIProvidersResponse>({});
  const [loading, setLoading] = useState(true);
  const [editingConfig, setEditingConfig] = useState<string | null>(null);
  const [tempConfig, setTempConfig] = useState<AIProviderConfig | null>(null);
  const [testResults, setTestResults] = useState<{ [key: string]: ConnectivityTestResponse }>({});
  const [testingConfigs, setTestingConfigs] = useState<Set<string>>(new Set());
  const [isCustomModel, setIsCustomModel] = useState(false);
  const [customModelId, setCustomModelId] = useState('');
  const [customModelName, setCustomModelName] = useState('');
  const [saveMessage, setSaveMessage] = useState<string>('');

  // 加载AI提供商列表
  useEffect(() => {
    const loadProviders = async () => {
      try {
        const data = await fetchAIProviders();
        setProviders(data);
      } catch (error) {
        console.error('Failed to load AI providers:', error);
      } finally {
        setLoading(false);
      }
    };

    loadProviders();
  }, []);

  // 开始编辑配置
  const startEditing = (providerId: string) => {
    const existing = configurations[providerId];
    const provider = providers[providerId];
    
    if (existing) {
      // 创建临时配置副本
      const tempConfigCopy = { ...existing };
      
      // 如果API密钥被掩码了，清空它要求重新输入
      if (tempConfigCopy.api_key && tempConfigCopy.api_key.includes('*')) {
        tempConfigCopy.api_key = '';
        console.log(`检测到掩码API密钥，已清空要求重新输入: ${providerId}`);
      }
      
      setTempConfig(tempConfigCopy);
      
      // 检查是否是自定义模型
      const isCustom = !provider?.models.find(m => m.id === existing.model_id);
      setIsCustomModel(isCustom);
      if (isCustom) {
        setCustomModelId(existing.model_id);
        setCustomModelName(existing.model_name);
      }
    } else {
      setTempConfig({
        provider_id: providerId,
        provider_name: provider?.name || '',
        model_id: provider?.models[0]?.id || '',
        model_name: provider?.models[0]?.name || '',
        base_url: provider?.default_base_url || '',
        api_key: '',
        enabled: true
      });
      setIsCustomModel(false);
      setCustomModelId('');
      setCustomModelName('');
    }
    setEditingConfig(providerId);
  };

  // 保存配置
  const saveConfiguration = () => {
    if (!tempConfig || !editingConfig) return;

    const newConfigurations = {
      ...configurations,
      [editingConfig]: tempConfig
    };

    onConfigurationChange(newConfigurations);
    setEditingConfig(null);
    setTempConfig(null);
    setSaveMessage('配置保存成功！');
    
    // 3秒后清除保存消息
    setTimeout(() => {
      setSaveMessage('');
    }, 3000);
  };

  // 删除配置
  const deleteConfiguration = (providerId: string) => {
    const newConfigurations = { ...configurations };
    delete newConfigurations[providerId];
    onConfigurationChange(newConfigurations);

    // 清除测试结果
    const newTestResults = { ...testResults };
    delete newTestResults[providerId];
    setTestResults(newTestResults);
  };

  // 测试连通性
  const testConnectivity = async (providerId: string) => {
    // 优先使用编辑状态中的临时配置，否则使用已保存的配置
    let config: AIProviderConfig;
    
    if (editingConfig === providerId && tempConfig) {
      // 如果正在编辑此配置，使用临时配置
      config = tempConfig;
    } else {
      // 否则使用已保存的配置
      config = configurations[providerId];
    }
    
    if (!config) {
      console.error('配置不存在:', providerId);
      return;
    }

    // 检查API Key是否被掩码了或为空
    if (!config.api_key || config.api_key.trim() === '') {
      setTestResults(prev => ({
        ...prev,
        [providerId]: {
          success: false,
          error: 'API密钥不能为空，请输入有效的API密钥',
          provider: config.provider_id,
          model: config.model_id,
          timestamp: new Date().toISOString()
        }
      }));
      return;
    }
    
    if (config.api_key.includes('***') || config.api_key.includes('*')) {
      setTestResults(prev => ({
        ...prev,
        [providerId]: {
          success: false,
          error: '检测到API密钥已被掩码处理，请点击"编辑"按钮重新输入完整的API密钥后再进行连通性测试',
          provider: config.provider_id,
          model: config.model_id,
          timestamp: new Date().toISOString()
        }
      }));
      return;
    }

    console.log('开始测试连通性:', providerId, config);
    setTestingConfigs(prev => new Set(prev).add(providerId));

    try {
      const testData = {
        provider: config.provider_id,
        model: config.model_id,
        base_url: config.base_url,
        api_key: config.api_key
      };
      
      console.log('发送测试请求:', testData);

      const result = await testAIConnectivity(testData);
      
      console.log('收到测试结果:', result);

      setTestResults(prev => ({
        ...prev,
        [providerId]: result
      }));
    } catch (error) {
      console.error('测试连通性失败:', error);
      
      // 提供更详细的错误信息
      let errorMessage = '连通性测试失败';
      if (error instanceof Error) {
        if (error.message.includes('fetch')) {
          errorMessage = '网络连接失败，请检查网络或代理设置';
        } else if (error.message.includes('timeout')) {
          errorMessage = '请求超时，请检查网络连接';
        } else if (error.message.includes('401')) {
          errorMessage = 'API密钥无效，请检查密钥是否正确';
        } else if (error.message.includes('404')) {
          errorMessage = 'API地址无效，请检查Base URL';
        } else if (error.message.includes('429')) {
          errorMessage = '请求过于频繁，请稍后重试';
        } else {
          errorMessage = error.message;
        }
      }
      
      setTestResults(prev => ({
        ...prev,
        [providerId]: {
          success: false,
          error: errorMessage,
          provider: config.provider_id,
          model: config.model_id,
          timestamp: new Date().toISOString()
        }
      }));
    } finally {
      setTestingConfigs(prev => {
        const newSet = new Set(prev);
        newSet.delete(providerId);
        return newSet;
      });
    }
  };

  // 模型选择改变时更新配置
  const handleModelChange = (modelId: string) => {
    if (!tempConfig || !editingConfig) return;

    const provider = providers[editingConfig];
    
    if (modelId === 'custom') {
      // 选择了自定义模型
      setIsCustomModel(true);
      setCustomModelId('');
      setCustomModelName('');
      setTempConfig({
        ...tempConfig,
        model_id: '',
        model_name: ''
      });
    } else {
      // 选择了预定义模型
      setIsCustomModel(false);
      const selectedModel = provider?.models.find(m => m.id === modelId);
      setTempConfig({
        ...tempConfig,
        model_id: modelId,
        model_name: selectedModel?.name || modelId
      });
    }
  };

  // 处理自定义模型输入
  const handleCustomModelChange = () => {
    if (!tempConfig || !customModelId.trim()) return;
    
    setTempConfig({
      ...tempConfig,
      model_id: customModelId.trim(),
      model_name: customModelName.trim() || customModelId.trim()
    });
  };

  if (loading) {
    return (
      <div className={`p-4 ${className}`}>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">加载AI提供商...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">AI模型配置</h3>
        <p className="text-sm text-gray-500">配置您要使用的AI服务提供商和模型</p>
      </div>

      {/* 已配置的服务 */}
      <div className="space-y-4">
        {Object.entries(configurations).map(([providerId, config]) => {
          const provider = providers[providerId];
          const testResult = testResults[providerId];
          const isTesting = testingConfigs.has(providerId);

          return (
            <div key={providerId} className="border border-gray-200 rounded-lg p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${config.enabled ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                  <div>
                    <h4 className="font-medium text-gray-900">{config.provider_name}</h4>
                    <p className="text-sm text-gray-500">{config.model_name}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => testConnectivity(providerId)}
                    disabled={isTesting}
                    className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                      isTesting
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                    }`}
                  >
                    {isTesting ? '测试中...' : '测试连通性'}
                  </button>
                  <button
                    onClick={() => startEditing(providerId)}
                    className="px-3 py-1 bg-gray-100 text-gray-700 rounded text-sm font-medium hover:bg-gray-200 transition-colors"
                  >
                    编辑
                  </button>
                  <button
                    onClick={() => deleteConfiguration(providerId)}
                    className="px-3 py-1 bg-red-100 text-red-700 rounded text-sm font-medium hover:bg-red-200 transition-colors"
                  >
                    删除
                  </button>
                </div>
              </div>

              {/* 测试结果 */}
              {testResult && (
                <div className={`p-3 rounded-md text-sm ${
                  testResult.success 
                    ? 'bg-green-50 border border-green-200' 
                    : 'bg-red-50 border border-red-200'
                }`}>
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${testResult.success ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className={`font-medium ${testResult.success ? 'text-green-800' : 'text-red-800'}`}>
                      {testResult.success ? '连接成功' : '连接失败'}
                    </span>
                  </div>
                  <p className={`mt-1 ${testResult.success ? 'text-green-700' : 'text-red-700'}`}>
                    {testResult.message || testResult.error}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(testResult.timestamp).toLocaleString()}
                  </p>
                </div>
              )}

              {/* 配置详情 */}
              <div className="text-sm text-gray-600 grid grid-cols-2 gap-2">
                <div>
                  <span className="font-medium">API地址：</span>
                  <span className="font-mono">{config.base_url}</span>
                </div>
                <div>
                  <span className="font-medium">API密钥：</span>
                  {config.api_key ? (
                    <div className="flex items-center space-x-2">
                      <span className="font-mono">
                        {config.api_key.includes('***') || config.api_key.includes('*') 
                          ? config.api_key 
                          : `${config.api_key.substring(0, 8)}...`}
                      </span>
                      {(config.api_key.includes('***') || config.api_key.includes('*')) && (
                        <span className="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded">
                          已掩码
                        </span>
                      )}
                    </div>
                  ) : (
                    <span className="text-red-500">未配置</span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 添加新配置 */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
        <h4 className="font-medium text-gray-900 mb-4">添加新的AI服务</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(providers).map(([providerId, provider]) => (
            <button
              key={providerId}
              onClick={() => startEditing(providerId)}
              disabled={!!configurations[providerId]}
              className={`p-3 border rounded-lg text-left transition-colors ${
                configurations[providerId]
                  ? 'border-gray-200 bg-gray-50 text-gray-400 cursor-not-allowed'
                  : 'border-gray-300 hover:border-blue-500 hover:bg-blue-50'
              }`}
            >
              <div className="font-medium text-sm">{provider.name}</div>
              <div className="text-xs text-gray-500 mt-1">{provider.description}</div>
              {configurations[providerId] && (
                <div className="text-xs text-green-600 mt-1">✓ 已配置</div>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* 配置编辑模态框 */}
      {editingConfig && tempConfig && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              配置 {providers[editingConfig]?.name}
            </h3>
            
            <div className="space-y-4">
              {/* 模型选择 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  选择模型
                </label>
                <select
                  value={isCustomModel ? 'custom' : tempConfig.model_id}
                  onChange={(e) => handleModelChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {providers[editingConfig]?.models.map((model) => (
                    <option key={model.id} value={model.id}>
                      {model.name} - {model.description}
                    </option>
                  ))}
                  <option value="custom">🔧 自定义模型</option>
                </select>
              </div>

              {/* 自定义模型输入 */}
              {isCustomModel && (
                <div className="space-y-3 p-3 bg-gray-50 rounded-md border border-gray-200">
                  <h4 className="text-sm font-medium text-gray-900">自定义模型配置</h4>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      模型ID *
                    </label>
                    <input
                      type="text"
                      value={customModelId}
                      onChange={(e) => {
                        setCustomModelId(e.target.value);
                        // 实时更新tempConfig
                        if (tempConfig) {
                          setTempConfig({
                            ...tempConfig,
                            model_id: e.target.value,
                            model_name: customModelName || e.target.value
                          });
                        }
                      }}
                      placeholder="例如: gpt-4-custom, claude-3-opus, 等"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      请输入准确的模型ID，这将用于API调用
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      模型显示名称（可选）
                    </label>
                    <input
                      type="text"
                      value={customModelName}
                      onChange={(e) => {
                        setCustomModelName(e.target.value);
                        // 实时更新tempConfig
                        if (tempConfig) {
                          setTempConfig({
                            ...tempConfig,
                            model_name: e.target.value || customModelId
                          });
                        }
                      }}
                      placeholder="例如: GPT-4 自定义版本"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      留空将使用模型ID作为显示名称
                    </p>
                  </div>
                </div>
              )}

              {/* API Base URL */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Base URL
                </label>
                <input
                  type="url"
                  value={tempConfig.base_url}
                  onChange={(e) => setTempConfig({ ...tempConfig, base_url: e.target.value })}
                  placeholder={providers[editingConfig]?.default_base_url}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  留空将使用默认地址：{providers[editingConfig]?.default_base_url}
                </p>
              </div>

              {/* API Key */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Key
                </label>
                <input
                  type="password"
                  value={tempConfig.api_key}
                  onChange={(e) => setTempConfig({ ...tempConfig, api_key: e.target.value })}
                  placeholder="输入您的API密钥"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {/* 检查原始配置是否有掩码API密钥 */}
                {configurations[editingConfig] && 
                 configurations[editingConfig].api_key && 
                 configurations[editingConfig].api_key.includes('*') && (
                  <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded-md">
                    <p className="text-sm text-yellow-800">
                      🔒 检测到已有API密钥（已掩码显示），如需修改请重新输入完整的API密钥
                    </p>
                  </div>
                )}
              </div>

              {/* 启用状态 */}
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="enabled"
                  checked={tempConfig.enabled}
                  onChange={(e) => setTempConfig({ ...tempConfig, enabled: e.target.checked })}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label htmlFor="enabled" className="ml-2 text-sm text-gray-700">
                  启用此配置
                </label>
              </div>

              {/* 测试结果显示 */}
              {testResults[editingConfig] && (
                <div className={`p-3 rounded-md text-sm ${
                  testResults[editingConfig].success 
                    ? 'bg-green-50 border border-green-200' 
                    : 'bg-red-50 border border-red-200'
                }`}>
                  <div className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${testResults[editingConfig].success ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className={`font-medium ${testResults[editingConfig].success ? 'text-green-800' : 'text-red-800'}`}>
                      {testResults[editingConfig].success ? '连接成功' : '连接失败'}
                    </span>
                  </div>
                  <p className={`mt-1 ${testResults[editingConfig].success ? 'text-green-700' : 'text-red-700'}`}>
                    {testResults[editingConfig].message || testResults[editingConfig].error}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(testResults[editingConfig].timestamp).toLocaleString()}
                  </p>
                </div>
              )}
            </div>

            <div className="flex justify-between items-center mt-6">
              {/* 左侧：测试连通性按钮 */}
              <button
                onClick={() => testConnectivity(editingConfig)}
                disabled={!tempConfig.api_key.trim() || testingConfigs.has(editingConfig)}
                className={`px-4 py-2 rounded-md transition-colors ${
                  tempConfig.api_key.trim() && !testingConfigs.has(editingConfig)
                    ? 'bg-green-600 text-white hover:bg-green-700'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                {testingConfigs.has(editingConfig) ? '测试中...' : '测试连通性'}
              </button>
              
              {/* 右侧：操作按钮 */}
              <div className="flex space-x-3">
                <button
                  onClick={() => {
                    setEditingConfig(null);
                    setTempConfig(null);
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                >
                  取消
                </button>
                <button
                  onClick={saveConfiguration}
                  disabled={!tempConfig.api_key.trim() || (isCustomModel && !customModelId.trim())}
                  className={`px-4 py-2 rounded-md transition-colors ${
                    tempConfig.api_key.trim() && (!isCustomModel || customModelId.trim())
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  保存配置
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 保存消息 */}
      {saveMessage && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm text-green-800">{saveMessage}</p>
        </div>
      )}
    </div>
  );
}; 