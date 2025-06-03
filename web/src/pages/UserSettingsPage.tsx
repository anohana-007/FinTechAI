import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  fetchUserSettings, 
  fetchUserSettingsDetail,
  updateUserSettings, 
  changePassword 
} from '../services/apiService';
import { UserSettingsData, ChangePasswordRequest, AIProviderConfig, ProxySettings } from '../types/types';
import { AIConfigurationPanel } from '../components/AIConfigurationPanel';
import { ProxyConfigurationPanel } from '../components/ProxyConfigurationPanel';

const UserSettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const { state } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'basic' | 'ai' | 'proxy' | 'password'>('basic');

  // 用户设置表单数据
  const [settings, setSettings] = useState<UserSettingsData>({
    tushare_token: '',
    email_sender_address: '',
    email_smtp_server: '',
    email_smtp_port: 587,
    email_smtp_user: '',
    email_smtp_password: '',
    ai_configurations: {},
    proxy_settings: {
      enabled: false,
      host: '',
      port: 8080,
      protocol: 'http'
    },
    preferred_llm: 'openai'
  });

  // 密码修改表单数据
  const [passwordData, setPasswordData] = useState<ChangePasswordRequest>({
    old_password: '',
    new_password: '',
  });
  const [confirmNewPassword, setConfirmNewPassword] = useState('');

  // 加载用户设置
  useEffect(() => {
    loadUserSettings();
  }, []);

  const loadUserSettings = async () => {
    try {
      setLoading(true);
      // 获取详细配置信息用于编辑
      const response = await fetchUserSettingsDetail();
      
      if (response.success) {
        setSettings({
          tushare_token: response.settings.tushare_token || '',
          email_sender_address: response.settings.email_sender_address || '',
          email_smtp_server: response.settings.email_smtp_server || '',
          email_smtp_port: response.settings.email_smtp_port || 587,
          email_smtp_user: response.settings.email_smtp_user || '',
          email_smtp_password: '', // 密码字段始终为空，用于新输入
          ai_configurations: response.settings.ai_configurations || {},
          proxy_settings: response.settings.proxy_settings || {
            enabled: false,
            host: '',
            port: 8080,
            protocol: 'http'
          },
          preferred_llm: response.settings.preferred_llm || 'openai'
        });
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : '加载设置失败');
    } finally {
      setLoading(false);
    }
  };

  const handleBasicSettingsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    if (name === 'email_smtp_port') {
      setSettings(prev => ({
        ...prev,
        [name]: parseInt(value) || 587,
      }));
    } else {
      setSettings(prev => ({
        ...prev,
        [name]: value,
      }));
    }

    if (error) setError('');
    if (success) setSuccess('');
  };

  const handleAIConfigurationChange = (configs: { [providerId: string]: AIProviderConfig }) => {
    console.log('AI配置更改:', configs); // 添加调试
    setSettings(prev => ({
      ...prev,
      ai_configurations: configs
    }));

    if (error) setError('');
    if (success) setSuccess('');
  };

  const handleProxySettingsChange = (proxySettings: ProxySettings) => {
    setSettings(prev => ({
      ...prev,
      proxy_settings: proxySettings
    }));

    if (error) setError('');
    if (success) setSuccess('');
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    if (name === 'confirm_new_password') {
      setConfirmNewPassword(value);
    } else {
      setPasswordData(prev => ({
        ...prev,
        [name]: value,
      }));
    }

    if (error) setError('');
    if (success) setSuccess('');
  };

  const validatePasswordForm = (): boolean => {
    if (!passwordData.old_password.trim()) {
      setError('请输入当前密码');
      return false;
    }
    if (!passwordData.new_password.trim()) {
      setError('请输入新密码');
      return false;
    }
    if (passwordData.new_password.length < 6) {
      setError('新密码至少需要6个字符');
      return false;
    }
    if (passwordData.new_password !== confirmNewPassword) {
      setError('两次输入的新密码不一致');
      return false;
    }
    return true;
  };

  const handleSaveSettings = async () => {
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      // 准备要保存的设置
      const settingsToSend: UserSettingsData = {};
      
      // 基础设置
      if (settings.tushare_token && settings.tushare_token !== '[已设置]') {
        settingsToSend.tushare_token = settings.tushare_token;
      }
      
      if (settings.email_sender_address) {
        settingsToSend.email_sender_address = settings.email_sender_address;
      }
      
      if (settings.email_smtp_server) {
        settingsToSend.email_smtp_server = settings.email_smtp_server;
      }
      
      if (settings.email_smtp_port) {
        settingsToSend.email_smtp_port = settings.email_smtp_port;
      }
      
      if (settings.email_smtp_user) {
        settingsToSend.email_smtp_user = settings.email_smtp_user;
      }
      
      if (settings.email_smtp_password) {
        settingsToSend.email_smtp_password = settings.email_smtp_password;
      }
      
      // AI配置
      if (settings.ai_configurations && Object.keys(settings.ai_configurations).length > 0) {
        console.log('AI配置数据:', settings.ai_configurations); // 添加调试
        settingsToSend.ai_configurations = settings.ai_configurations;
      } else {
        console.log('没有AI配置数据或数据为空'); // 添加调试
      }
      
      // 代理设置
      if (settings.proxy_settings) {
        settingsToSend.proxy_settings = settings.proxy_settings;
      }

      console.log('准备保存的设置:', settingsToSend); // 添加调试日志

      await updateUserSettings(settingsToSend);
      setSuccess('设置保存成功');
      
      // 清空密码字段，因为已经保存了
      if (settings.email_smtp_password) {
        setSettings(prev => ({
          ...prev,
          email_smtp_password: ''
        }));
      }

      // 根据不同标签页处理保存后的状态更新
      if (activeTab === 'basic') {
        // 基础配置标签页：重新加载所有设置
        await loadUserSettings();
      } else if (activeTab === 'proxy') {
        // 代理配置标签页：部分更新，避免掩码问题
        const response = await fetchUserSettingsDetail();
        if (response.success) {
          setSettings(prev => ({
            ...prev,
            proxy_settings: response.settings.proxy_settings || {
              enabled: false,
              host: '',
              port: 8080,
              protocol: 'http'
            }
          }));
        }
      } else if (activeTab === 'ai') {
        // AI配置标签页：保持当前状态避免显示掩码
        // 不重新加载，因为会显示掩码的API密钥
      }
    } catch (error) {
      console.error('保存设置失败:', error); // 添加调试日志
      setError(error instanceof Error ? error.message : '保存设置失败');
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validatePasswordForm()) {
      return;
    }

    setChangingPassword(true);
    setError('');
    setSuccess('');

    try {
      await changePassword(passwordData);
      setSuccess('密码修改成功');
      
      // 清空密码表单
      setPasswordData({ old_password: '', new_password: '' });
      setConfirmNewPassword('');
    } catch (error) {
      setError(error instanceof Error ? error.message : '修改密码失败');
    } finally {
      setChangingPassword(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-lg">加载用户设置中...</span>
      </div>
    );
  }

  const tabs = [
    { id: 'basic', name: '基础配置', icon: '⚙️' },
    { id: 'ai', name: 'AI模型配置', icon: '🤖' },
    { id: 'proxy', name: '代理配置', icon: '🌐' },
    { id: 'password', name: '密码修改', icon: '🔒' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* 导航区域 */}
        <div className="mb-6">
          <nav className="flex items-center space-x-2 text-sm text-gray-500 mb-4">
            <button
              onClick={() => navigate('/')}
              className="hover:text-gray-700 transition-colors"
            >
              首页
            </button>
            <span>/</span>
            <span className="text-gray-900">用户设置</span>
          </nav>
          
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900">用户设置</h1>
            <button
              onClick={() => navigate('/')}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              返回主页
            </button>
          </div>
        </div>

        {/* 用户信息显示 */}
        <div className="mb-6 p-4 bg-white border border-gray-200 rounded-lg shadow-sm">
          <h3 className="text-sm font-medium text-gray-700 mb-2">当前用户</h3>
          <p className="text-sm text-gray-600">
            用户名: <span className="font-medium">{state.user?.username}</span> | 
            邮箱: <span className="font-medium">{state.user?.email}</span>
          </p>
        </div>

        {/* 错误和成功消息 */}
        {error && (
          <div className="mb-6 rounded-md bg-red-50 border border-red-200 p-4">
            <div className="flex items-center">
              <div className="text-red-500 mr-3">❌</div>
              <div className="text-sm text-red-700">{error}</div>
            </div>
          </div>
        )}
        
        {success && (
          <div className="mb-6 rounded-md bg-green-50 border border-green-200 p-4">
            <div className="flex items-center">
              <div className="text-green-500 mr-3">✅</div>
              <div className="text-sm text-green-700">{success}</div>
            </div>
          </div>
        )}

        {/* 标签页导航 */}
        <div className="bg-white shadow rounded-lg">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as typeof activeTab)}
                  className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {/* 基础配置标签页 */}
            {activeTab === 'basic' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Tushare 配置</h3>
                  <div>
                    <label htmlFor="tushare_token" className="block text-sm font-medium text-gray-700">
                      Tushare Token
                    </label>
                    <input
                      type="text"
                      name="tushare_token"
                      id="tushare_token"
                      value={settings.tushare_token}
                      onChange={handleBasicSettingsChange}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder={settings.tushare_token ? "当前已配置（显示已掩码）" : "请输入您的Tushare Token"}
                    />
                    <p className="mt-2 text-sm text-gray-500">
                      用于获取股票数据，请在 <a href="https://tushare.pro" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-500">Tushare官网</a> 注册获取
                      {settings.tushare_token && settings.tushare_token.includes('*') && (
                        <span className="block text-green-600 mt-1">✓ 当前已配置Token</span>
                      )}
                    </p>
                  </div>
                </div>

                {/* 邮件配置 */}
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">邮件发送配置</h3>
                  <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                    <div>
                      <label htmlFor="email_sender_address" className="block text-sm font-medium text-gray-700">
                        发件人邮箱地址
                      </label>
                      <input
                        type="email"
                        name="email_sender_address"
                        id="email_sender_address"
                        value={settings.email_sender_address}
                        onChange={handleBasicSettingsChange}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        placeholder="sender@example.com"
                      />
                      {settings.email_sender_address && (
                        <p className="mt-1 text-sm text-green-600">✓ 已配置</p>
                      )}
                    </div>

                    <div>
                      <label htmlFor="email_smtp_server" className="block text-sm font-medium text-gray-700">
                        SMTP 服务器
                      </label>
                      <input
                        type="text"
                        name="email_smtp_server"
                        id="email_smtp_server"
                        value={settings.email_smtp_server}
                        onChange={handleBasicSettingsChange}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        placeholder="smtp.qq.com"
                      />
                      {settings.email_smtp_server && (
                        <p className="mt-1 text-sm text-green-600">✓ 已配置</p>
                      )}
                    </div>

                    <div>
                      <label htmlFor="email_smtp_port" className="block text-sm font-medium text-gray-700">
                        SMTP 端口
                      </label>
                      <input
                        type="number"
                        name="email_smtp_port"
                        id="email_smtp_port"
                        value={settings.email_smtp_port}
                        onChange={handleBasicSettingsChange}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        placeholder="587"
                      />
                    </div>

                    <div>
                      <label htmlFor="email_smtp_user" className="block text-sm font-medium text-gray-700">
                        SMTP 用户名
                      </label>
                      <input
                        type="text"
                        name="email_smtp_user"
                        id="email_smtp_user"
                        value={settings.email_smtp_user}
                        onChange={handleBasicSettingsChange}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        placeholder="用户名"
                      />
                      {settings.email_smtp_user && (
                        <p className="mt-1 text-sm text-green-600">✓ 已配置</p>
                      )}
                    </div>

                    <div className="sm:col-span-2">
                      <label htmlFor="email_smtp_password" className="block text-sm font-medium text-gray-700">
                        SMTP 密码
                      </label>
                      <input
                        type="password"
                        name="email_smtp_password"
                        id="email_smtp_password"
                        value={settings.email_smtp_password}
                        onChange={handleBasicSettingsChange}
                        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        placeholder="请输入SMTP密码"
                      />
                      <p className="mt-2 text-sm text-gray-500">
                        {settings.email_smtp_password ? (
                          <span>已输入新密码，保存后将更新</span>
                        ) : (
                          <>
                            为了安全，密码不会显示已保存的值。
                            <span className="block text-green-600 mt-1">
                              ✓ 当前已配置密码，如需修改请重新输入
                            </span>
                          </>
                        )}
                      </p>
                    </div>
                  </div>
                </div>

                {/* 保存按钮 */}
                <div className="flex justify-end pt-4 border-t border-gray-200">
                  <button
                    onClick={handleSaveSettings}
                    disabled={saving}
                    className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                  >
                    {saving ? '保存中...' : '保存基础设置'}
                  </button>
                </div>
              </div>
            )}

            {/* AI配置标签页 */}
            {activeTab === 'ai' && (
              <div>
                <AIConfigurationPanel
                  configurations={settings.ai_configurations || {}}
                  onConfigurationChange={handleAIConfigurationChange}
                />
                
                {/* 保存按钮 */}
                <div className="flex justify-end pt-6 border-t border-gray-200 mt-6">
                  <button
                    onClick={handleSaveSettings}
                    disabled={saving}
                    className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                  >
                    {saving ? '保存中...' : '保存AI配置'}
                  </button>
                </div>
              </div>
            )}

            {/* 代理配置标签页 */}
            {activeTab === 'proxy' && (
              <div>
                <ProxyConfigurationPanel
                  proxySettings={settings.proxy_settings || { enabled: false, host: '', port: 8080, protocol: 'http' }}
                  onProxySettingsChange={handleProxySettingsChange}
                />
                
                {/* 保存按钮 */}
                <div className="flex justify-end pt-6 border-t border-gray-200 mt-6">
                  <button
                    onClick={handleSaveSettings}
                    disabled={saving}
                    className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                  >
                    {saving ? '保存中...' : '保存代理设置'}
                  </button>
                </div>
              </div>
            )}

            {/* 密码修改标签页 */}
            {activeTab === 'password' && (
              <div className="max-w-md">
                <h3 className="text-lg font-medium text-gray-900 mb-4">修改密码</h3>
                <form onSubmit={handleChangePassword} className="space-y-4">
                  <div>
                    <label htmlFor="old_password" className="block text-sm font-medium text-gray-700">
                      当前密码
                    </label>
                    <input
                      type="password"
                      name="old_password"
                      id="old_password"
                      value={passwordData.old_password}
                      onChange={handlePasswordChange}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="请输入当前密码"
                    />
                  </div>

                  <div>
                    <label htmlFor="new_password" className="block text-sm font-medium text-gray-700">
                      新密码
                    </label>
                    <input
                      type="password"
                      name="new_password"
                      id="new_password"
                      value={passwordData.new_password}
                      onChange={handlePasswordChange}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="请输入新密码（至少6个字符）"
                    />
                  </div>

                  <div>
                    <label htmlFor="confirm_new_password" className="block text-sm font-medium text-gray-700">
                      确认新密码
                    </label>
                    <input
                      type="password"
                      name="confirm_new_password"
                      id="confirm_new_password"
                      value={confirmNewPassword}
                      onChange={handlePasswordChange}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="请再次输入新密码"
                    />
                  </div>

                  <div className="flex justify-end pt-4">
                    <button
                      type="submit"
                      disabled={changingPassword}
                      className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                    >
                      {changingPassword ? '修改中...' : '修改密码'}
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserSettingsPage; 