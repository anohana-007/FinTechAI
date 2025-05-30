import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { 
  fetchUserSettings, 
  updateUserSettings, 
  changePassword 
} from '../services/apiService';
import { UserSettingsData, ChangePasswordRequest } from '../types/types';

const UserSettingsPage: React.FC = () => {
  const { state } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [changingPassword, setChangingPassword] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  // 用户设置表单数据
  const [settings, setSettings] = useState<UserSettingsData>({
    tushare_token: '',
    email_sender_address: '',
    email_smtp_server: '',
    email_smtp_port: 587,
    email_smtp_user: '',
    email_smtp_password: '',
    ai_api_keys: {
      openai: '',
      gemini: '',
      deepseek: '',
    },
  });

  // 密码修改表单数据
  const [passwordData, setPasswordData] = useState<ChangePasswordRequest>({
    old_password: '',
    new_password: '',
  });
  const [confirmNewPassword, setConfirmNewPassword] = useState('');

  // 显示/隐藏密码修改区域
  const [showPasswordForm, setShowPasswordForm] = useState(false);

  // 加载用户设置
  useEffect(() => {
    loadUserSettings();
  }, []);

  const loadUserSettings = async () => {
    try {
      setLoading(true);
      const response = await fetchUserSettings();
      
      if (response.success) {
        setSettings({
          tushare_token: response.settings.has_tushare_token ? '[已设置]' : '',
          email_sender_address: response.settings.email_sender_address || '',
          email_smtp_server: response.settings.email_smtp_server || '',
          email_smtp_port: response.settings.email_smtp_port || 587,
          email_smtp_user: response.settings.email_smtp_user || '',
          email_smtp_password: '', // 不从后端获取密码
          ai_api_keys: {
            openai: '',
            gemini: '',
            deepseek: '',
          },
        });
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : '加载设置失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSettingsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    if (name.startsWith('ai_')) {
      const aiProvider = name.replace('ai_', '');
      setSettings(prev => ({
        ...prev,
        ai_api_keys: {
          ...prev.ai_api_keys,
          [aiProvider]: value,
        },
      }));
    } else if (name === 'email_smtp_port') {
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

  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      // 过滤空值
      const settingsToSend: UserSettingsData = {};
      
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
      
      // 处理AI API Keys
      const ai_keys: { [key: string]: string } = {};
      if (settings.ai_api_keys?.openai) ai_keys.openai = settings.ai_api_keys.openai;
      if (settings.ai_api_keys?.gemini) ai_keys.gemini = settings.ai_api_keys.gemini;
      if (settings.ai_api_keys?.deepseek) ai_keys.deepseek = settings.ai_api_keys.deepseek;
      
      if (Object.keys(ai_keys).length > 0) {
        settingsToSend.ai_api_keys = ai_keys;
      }

      await updateUserSettings(settingsToSend);
      setSuccess('设置保存成功');
      
      // 重新加载设置以更新状态
      await loadUserSettings();
    } catch (error) {
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
      setShowPasswordForm(false);
    } catch (error) {
      setError(error instanceof Error ? error.message : '修改密码失败');
    } finally {
      setChangingPassword(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">加载用户设置中...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-6">用户设置</h2>
            
            {/* 用户信息显示 */}
            <div className="mb-6 p-4 bg-gray-50 rounded-md">
              <h3 className="text-sm font-medium text-gray-700 mb-2">当前用户</h3>
              <p className="text-sm text-gray-600">
                用户名: {state.user?.username} | 邮箱: {state.user?.email}
              </p>
            </div>

            {/* 错误和成功消息 */}
            {error && (
              <div className="mb-4 rounded-md bg-red-50 p-4">
                <div className="text-sm text-red-700">{error}</div>
              </div>
            )}
            
            {success && (
              <div className="mb-4 rounded-md bg-green-50 p-4">
                <div className="text-sm text-green-700">{success}</div>
              </div>
            )}

            {/* 用户设置表单 */}
            <form onSubmit={handleSaveSettings} className="space-y-6">
              {/* Tushare配置 */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Tushare 配置</h3>
                <div>
                  <label htmlFor="tushare_token" className="block text-sm font-medium text-gray-700">
                    Tushare Token
                  </label>
                  <input
                    type="password"
                    name="tushare_token"
                    id="tushare_token"
                    value={settings.tushare_token}
                    onChange={handleSettingsChange}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="请输入您的Tushare Token"
                  />
                  <p className="mt-2 text-sm text-gray-500">
                    用于获取股票数据，请在 <a href="https://tushare.pro" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-500">Tushare官网</a> 注册获取
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
                      onChange={handleSettingsChange}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="sender@example.com"
                    />
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
                      onChange={handleSettingsChange}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="smtp.qq.com"
                    />
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
                      onChange={handleSettingsChange}
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
                      onChange={handleSettingsChange}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="用户名"
                    />
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
                      onChange={handleSettingsChange}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="请输入SMTP密码"
                    />
                    <p className="mt-2 text-sm text-gray-500">
                      注意：为了安全，密码不会显示已保存的值。如需修改，请重新输入。
                    </p>
                  </div>
                </div>
              </div>

              {/* AI API Keys配置 */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">AI API Keys 配置</h3>
                <div className="space-y-4">
                  <div>
                    <label htmlFor="ai_openai" className="block text-sm font-medium text-gray-700">
                      OpenAI GPT API Key
                    </label>
                    <input
                      type="password"
                      name="ai_openai"
                      id="ai_openai"
                      value={settings.ai_api_keys?.openai || ''}
                      onChange={handleSettingsChange}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="sk-..."
                    />
                  </div>

                  <div>
                    <label htmlFor="ai_gemini" className="block text-sm font-medium text-gray-700">
                      Google Gemini API Key
                    </label>
                    <input
                      type="password"
                      name="ai_gemini"
                      id="ai_gemini"
                      value={settings.ai_api_keys?.gemini || ''}
                      onChange={handleSettingsChange}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="您的Gemini API Key"
                    />
                  </div>

                  <div>
                    <label htmlFor="ai_deepseek" className="block text-sm font-medium text-gray-700">
                      DeepSeek API Key
                    </label>
                    <input
                      type="password"
                      name="ai_deepseek"
                      id="ai_deepseek"
                      value={settings.ai_api_keys?.deepseek || ''}
                      onChange={handleSettingsChange}
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="sk-..."
                    />
                  </div>
                </div>
                <p className="mt-2 text-sm text-gray-500">
                  AI API Keys用于生成股票分析。至少配置一个即可使用AI分析功能。
                </p>
              </div>

              {/* 保存按钮 */}
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={saving}
                  className="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {saving ? '保存中...' : '保存设置'}
                </button>
              </div>
            </form>

            {/* 密码修改区域 */}
            <div className="mt-8 pt-8 border-t border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">修改密码</h3>
                <button
                  type="button"
                  onClick={() => setShowPasswordForm(!showPasswordForm)}
                  className="text-sm text-indigo-600 hover:text-indigo-500"
                >
                  {showPasswordForm ? '取消' : '修改密码'}
                </button>
              </div>

              {showPasswordForm && (
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

                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={changingPassword}
                      className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
                    >
                      {changingPassword ? '修改中...' : '修改密码'}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserSettingsPage; 