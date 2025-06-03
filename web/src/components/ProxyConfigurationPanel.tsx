import React, { useState } from 'react';
import { ProxySettings, ProxyTestResult } from '../types/types';
import { testProxyConnectivity, validateProxySettings } from '../services/apiService';

interface ProxyConfigurationPanelProps {
  proxySettings: ProxySettings;
  onProxySettingsChange: (settings: ProxySettings) => void;
  className?: string;
}

export const ProxyConfigurationPanel: React.FC<ProxyConfigurationPanelProps> = ({
  proxySettings,
  onProxySettingsChange,
  className = ''
}) => {
  const [settings, setSettings] = useState<ProxySettings>(proxySettings);
  const [showPassword, setShowPassword] = useState(false);
  const [testResult, setTestResult] = useState<ProxyTestResult | null>(null);
  const [isTesting, setIsTesting] = useState(false);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  // 更新设置并通知父组件
  const updateSettings = (newSettings: Partial<ProxySettings>) => {
    const updatedSettings = { ...settings, ...newSettings };
    setSettings(updatedSettings);
    onProxySettingsChange(updatedSettings);
    
    // 清除之前的测试结果和验证错误
    if (testResult) setTestResult(null);
    if (validationErrors.length > 0) setValidationErrors([]);
  };

  // 验证代理设置
  const validateSettings = async (): Promise<boolean> => {
    try {
      const result = await validateProxySettings(settings);
      if (!result.valid) {
        setValidationErrors(result.errors || []);
        return false;
      }
      setValidationErrors([]);
      return true;
    } catch (error) {
      setValidationErrors([error instanceof Error ? error.message : '验证失败']);
      return false;
    }
  };

  // 测试代理连接
  const testProxyConnection = async () => {
    if (!settings.enabled) {
      setValidationErrors(['请先启用代理']);
      return;
    }

    // 先验证设置
    const isValid = await validateSettings();
    if (!isValid) {
      return;
    }

    setIsTesting(true);
    setTestResult(null);

    try {
      const result = await testProxyConnectivity(settings);
      setTestResult(result);
    } catch (error) {
      setTestResult({
        success: false,
        error: error instanceof Error ? error.message : '连接测试失败',
        timestamp: new Date().toISOString()
      });
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">代理配置</h3>
        <p className="text-sm text-gray-500">配置网络代理以访问AI服务</p>
      </div>

      {/* 启用代理开关 */}
      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
        <div>
          <h4 className="font-medium text-gray-900">启用代理</h4>
          <p className="text-sm text-gray-500">通过代理服务器访问AI API</p>
        </div>
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={settings.enabled}
            onChange={(e) => updateSettings({ enabled: e.target.checked })}
            className="sr-only"
          />
          <div className={`w-11 h-6 rounded-full transition-colors ${
            settings.enabled ? 'bg-blue-600' : 'bg-gray-300'
          }`}>
            <div className={`w-5 h-5 bg-white rounded-full shadow transition-transform ${
              settings.enabled ? 'translate-x-5' : 'translate-x-0'
            } mt-0.5 ml-0.5`}></div>
          </div>
        </label>
      </div>

      {/* 代理配置详情 */}
      {settings.enabled && (
        <div className="space-y-4 p-4 border border-gray-200 rounded-lg">
          {/* 协议选择 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              代理协议
            </label>
            <select
              value={settings.protocol || 'http'}
              onChange={(e) => updateSettings({ protocol: e.target.value as 'http' | 'https' | 'socks5' })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="http">HTTP</option>
              <option value="https">HTTPS</option>
              <option value="socks5">SOCKS5</option>
            </select>
          </div>

          {/* 代理服务器配置 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                代理服务器地址
              </label>
              <input
                type="text"
                value={settings.host}
                onChange={(e) => updateSettings({ host: e.target.value })}
                placeholder="例如: proxy.example.com 或 127.0.0.1"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                端口
              </label>
              <input
                type="number"
                value={settings.port}
                onChange={(e) => updateSettings({ port: parseInt(e.target.value) || 0 })}
                placeholder="8080"
                min="1"
                max="65535"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* 代理身份验证 */}
          <div className="border-t pt-4">
            <h4 className="font-medium text-gray-900 mb-3">身份验证（可选）</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  用户名
                </label>
                <input
                  type="text"
                  value={settings.username || ''}
                  onChange={(e) => updateSettings({ username: e.target.value })}
                  placeholder="代理用户名（如果需要）"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  密码
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={settings.password || ''}
                    onChange={(e) => updateSettings({ password: e.target.value })}
                    placeholder="代理密码（如果需要）"
                    className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? (
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                      </svg>
                    ) : (
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* 代理配置预览 */}
          <div className="bg-gray-50 p-3 rounded-md">
            <h5 className="text-sm font-medium text-gray-700 mb-2">代理配置预览</h5>
            <div className="text-sm text-gray-600 font-mono">
              {settings.protocol || 'http'}://
              {settings.username && settings.password && (
                <span>{settings.username}:***@</span>
              )}
              {settings.host || 'proxy.example.com'}:{settings.port || 8080}
            </div>
          </div>

          {/* 测试连接按钮 */}
          <div className="flex justify-end space-x-3">
            <button
              onClick={validateSettings}
              disabled={!settings.enabled}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                settings.enabled
                  ? 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              验证配置
            </button>
            <button
              onClick={testProxyConnection}
              disabled={!settings.host || !settings.port || isTesting}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                settings.host && settings.port && !isTesting
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              {isTesting ? (
                <span className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  测试中...
                </span>
              ) : (
                '测试代理连接'
              )}
            </button>
          </div>

          {/* 验证错误显示 */}
          {validationErrors.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <h5 className="text-sm font-medium text-red-800 mb-2">配置验证失败</h5>
              <ul className="text-sm text-red-700 space-y-1">
                {validationErrors.map((error, index) => (
                  <li key={index}>• {error}</li>
                ))}
              </ul>
            </div>
          )}

          {/* 测试结果显示 */}
          {testResult && (
            <div className={`p-4 rounded-md border ${
              testResult.success
                ? 'bg-green-50 border-green-200'
                : 'bg-red-50 border-red-200'
            }`}>
              <div className="flex items-center space-x-2 mb-3">
                <div className={`w-3 h-3 rounded-full ${
                  testResult.success ? 'bg-green-500' : 'bg-red-500'
                }`}></div>
                <h5 className={`font-medium ${
                  testResult.success ? 'text-green-800' : 'text-red-800'
                }`}>
                  {testResult.success ? '连接测试成功' : '连接测试失败'}
                </h5>
              </div>

              <p className={`text-sm mb-3 ${
                testResult.success ? 'text-green-700' : 'text-red-700'
              }`}>
                {testResult.message || testResult.error}
              </p>

              {/* 代理配置信息 */}
              {testResult.proxy_config && (
                <div className="text-sm text-gray-600 mb-3">
                  <span className="font-medium">测试配置：</span>
                  <span className="font-mono">
                    {testResult.proxy_config.protocol}://{testResult.proxy_config.host}:{testResult.proxy_config.port}
                  </span>
                  {testResult.proxy_config.has_auth && (
                    <span className="text-green-600 ml-2">✓ 已认证</span>
                  )}
                </div>
              )}

              {/* 详细测试结果 */}
              {testResult.test_results && testResult.test_results.length > 0 && (
                <div className="space-y-2">
                  <h6 className="text-sm font-medium text-gray-700">详细测试结果:</h6>
                  {testResult.test_results.map((test, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-white rounded border">
                      <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${
                          test.success ? 'bg-green-500' : 'bg-red-500'
                        }`}></div>
                        <span className="text-sm font-medium">{test.test}</span>
                      </div>
                      <div className="text-sm text-gray-600">
                        {test.success ? (
                          test.response_time ? `${test.response_time}ms` : '成功'
                        ) : (
                          <span className="text-red-600">{test.error}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* 测试摘要 */}
              {testResult.summary && (
                <div className="mt-3 p-2 bg-white rounded border text-sm">
                  <div className="grid grid-cols-2 gap-2 text-gray-600">
                    <div>总测试: {testResult.summary.total_tests}</div>
                    <div className="text-green-600">成功: {testResult.summary.successful_tests}</div>
                    <div className="text-red-600">失败: {testResult.summary.failed_tests}</div>
                    <div>平均延迟: {testResult.summary.average_response_time}ms</div>
                  </div>
                </div>
              )}

              <div className="text-xs text-gray-500 mt-2">
                测试时间: {new Date(testResult.timestamp).toLocaleString()}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 代理说明 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">代理配置说明</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• 代理配置将应用于所有AI API请求</li>
          <li>• 支持HTTP、HTTPS和SOCKS5代理协议</li>
          <li>• 如果您的代理需要身份验证，请填写用户名和密码</li>
          <li>• 代理设置将被加密存储，保护您的隐私</li>
          <li>• 可以随时禁用代理或更改配置</li>
        </ul>
      </div>

      {/* 常见代理配置示例 */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-2">常见配置示例</h4>
        <div className="space-y-2 text-sm text-gray-600">
          <div>
            <span className="font-medium">本地代理：</span>
            <span className="font-mono ml-1">127.0.0.1:1080 (SOCKS5)</span>
          </div>
          <div>
            <span className="font-medium">HTTP代理：</span>
            <span className="font-mono ml-1">proxy.company.com:8080 (HTTP)</span>
          </div>
          <div>
            <span className="font-medium">科学上网：</span>
            <span className="font-mono ml-1">localhost:7890 (HTTP/SOCKS5)</span>
          </div>
        </div>
      </div>
    </div>
  );
}; 