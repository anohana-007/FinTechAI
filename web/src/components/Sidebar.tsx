import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { NavItem } from './NavItem';

interface SidebarProps {
  onNavigate?: (page: 'dashboard' | 'alert-log' | 'settings') => void;
  currentPage?: 'dashboard' | 'alert-log' | 'settings';
}

const Sidebar: React.FC<SidebarProps> = ({ onNavigate, currentPage = 'dashboard' }) => {
  const { state, logout } = useAuth();

  // 认证用户的导航项
  const authenticatedNavItems = [
    {
      icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M7.5 15.8333V10.8333C7.5 10.3913 7.3244 9.96738 7.01184 9.65482C6.69928 9.34226 6.27536 9.16667 5.83333 9.16667H4.16667C3.72464 9.16667 3.30072 9.34226 2.98816 9.65482C2.67559 9.96738 2.5 10.3913 2.5 10.8333V15.8333C2.5 16.2754 2.67559 16.6993 2.98816 17.0118C3.30072 17.3244 3.72464 17.5 4.16667 17.5H5.83333C6.27536 17.5 6.69928 17.3244 7.01184 17.0118C7.3244 16.6993 7.5 16.2754 7.5 15.8333Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
      label: '仪表盘',
      page: 'dashboard' as const
    },
    {
      icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M10 6.66667V10L12.5 12.5M17.5 10C17.5 14.1421 14.1421 17.5 10 17.5C5.85786 17.5 2.5 14.1421 2.5 10C2.5 5.85786 5.85786 2.5 10 2.5C14.1421 2.5 17.5 5.85786 17.5 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
      label: '历史告警',
      page: 'alert-log' as const
    },
    {
      icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8.60417 3.5975C8.95917 2.13417 11.0408 2.13417 11.3958 3.5975M17.5 10C17.5 14.1421 14.1421 17.5 10 17.5C5.85786 17.5 2.5 14.1421 2.5 10C2.5 5.85786 5.85786 2.5 10 2.5C14.1421 2.5 17.5 5.85786 17.5 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
      label: '用户设置',
      page: 'settings' as const
    }
  ];

  // 未认证用户的导航项
  const unauthenticatedNavItems = [
    {
      icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3.33333 6.66667C3.33333 5.78261 3.68452 4.93477 4.30964 4.30964C4.93477 3.68452 5.78261 3.33333 6.66667 3.33333H13.3333C14.2174 3.33333 15.0652 3.68452 15.6904 4.30964C16.3155 4.93477 16.6667 5.78261 16.6667 6.66667V13.3333C16.6667 14.2174 16.3155 15.0652 15.6904 15.6904C15.0652 16.3155 14.2174 16.6667 13.3333 16.6667H6.66667C5.78261 16.6667 4.93477 16.3155 4.30964 15.6904C3.68452 15.0652 3.33333 14.2174 3.33333 13.3333V6.66667Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path><path d="M8.33333 8.33333L13.3333 10L8.33333 11.6667V8.33333Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
      label: '演示模式',
      page: 'dashboard' as const
    }
  ];

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('登出失败:', error);
    }
  };

  const navItems = state.isAuthenticated ? authenticatedNavItems : unauthenticatedNavItems;

  return (
    <nav className="absolute top-0 left-0 p-6 w-64 bg-white border-r border-solid border-r-neutral-200 h-[874px] max-md:relative max-md:p-4 max-md:w-full max-md:h-auto max-sm:px-2 max-sm:py-4">
      <h1 className="mb-8 text-xl font-semibold leading-8 text-black">
        FinTech AI
      </h1>
      
      {/* 用户信息区域 */}
      {state.isAuthenticated && state.user && (
        <div className="mb-6 p-3 bg-gray-50 rounded-lg">
          <div className="text-sm font-medium text-gray-900">{state.user.username}</div>
          <div className="text-xs text-gray-500">{state.user.email}</div>
        </div>
      )}

      <button className="flex justify-center items-center mb-8 w-8 h-8 rounded bg-neutral-100">
        <div
          dangerouslySetInnerHTML={{
            __html:
              '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2.6665 4H13.3332M2.6665 8H13.3332M2.6665 12H13.3332" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
          }}
        />
      </button>
      
      {/* 导航项 */}
      {navItems.map((item, index) => (
        <NavItem 
          key={index} 
          icon={item.icon}
          label={item.label}
          isActive={item.page ? currentPage === item.page : false}
          onClick={item.page ? () => onNavigate?.(item.page!) : undefined}
        />
      ))}

      {/* 登录/登出按钮 */}
      {state.isAuthenticated ? (
        <div className="mt-8 pt-4 border-t border-gray-200">
          <button
            onClick={handleLogout}
            className="flex items-center w-full p-2 text-left text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <div
              className="mr-3"
              dangerouslySetInnerHTML={{
                __html: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13.3333 14.1667L17.5 10L13.3333 5.83333M17.5 10H7.5M7.5 2.5H5.83333C5.39131 2.5 4.96738 2.67559 4.65482 2.98816C4.34226 3.30072 4.16667 3.72464 4.16667 4.16667V15.8333C4.16667 16.2754 4.34226 16.6993 4.65482 17.0118C4.96738 17.3244 5.39131 17.5 5.83333 17.5H7.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>'
              }}
            />
            登出
          </button>
        </div>
      ) : (
        <div className="mt-8 pt-4 border-t border-gray-200 space-y-2">
          <button
            onClick={() => window.location.href = '/login'}
            className="flex items-center w-full p-2 text-left text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
          >
            <div
              className="mr-3"
              dangerouslySetInnerHTML={{
                __html: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M6.66667 14.1667L2.5 10L6.66667 5.83333M2.5 10H12.5M12.5 2.5H14.1667C14.6087 2.5 15.0326 2.67559 15.3452 2.98816C15.6577 3.30072 15.8333 3.72464 15.8333 4.16667V15.8333C15.8333 16.2754 15.6577 16.6993 15.3452 17.0118C15.0326 17.3244 14.6087 17.5 14.1667 17.5H12.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>'
              }}
            />
            登录
          </button>
          <button
            onClick={() => window.location.href = '/register'}
            className="flex items-center w-full p-2 text-left text-green-600 hover:bg-green-50 rounded-lg transition-colors"
          >
            <div
              className="mr-3"
              dangerouslySetInnerHTML={{
                __html: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13.3333 5.83333V4.16667C13.3333 3.72464 13.1577 3.30072 12.8452 2.98816C12.5326 2.67559 12.1087 2.5 11.6667 2.5H4.16667C3.72464 2.5 3.30072 2.67559 2.98816 2.98816C2.67559 3.30072 2.5 3.72464 2.5 4.16667V15.8333C2.5 16.2754 2.67559 16.6993 2.98816 17.0118C3.30072 17.3244 3.72464 17.5 4.16667 17.5H11.6667C12.1087 17.5 12.5326 17.3244 12.8452 17.0118C13.1577 16.6993 13.3333 16.2754 13.3333 15.8333V14.1667M10.8333 6.66667L15.8333 10M15.8333 10L10.8333 13.3333M15.8333 10H5.83333" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>'
              }}
            />
            注册
          </button>
        </div>
      )}
    </nav>
  );
};

export { Sidebar }; 