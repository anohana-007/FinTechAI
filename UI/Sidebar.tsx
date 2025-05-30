import React from 'react';
import { NavItem } from './NavItem';

const navItems = [
  {
    icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M7.5 15.8333V10.8333C7.5 10.3913 7.3244 9.96738 7.01184 9.65482C6.69928 9.34226 6.27536 9.16667 5.83333 9.16667H4.16667C3.72464 9.16667 3.30072 9.34226 2.98816 9.65482C2.67559 9.96738 2.5 10.3913 2.5 10.8333V15.8333C2.5 16.2754 2.67559 16.6993 2.98816 17.0118C3.30072 17.3244 3.72464 17.5 4.16667 17.5H5.83333C6.27536 17.5 6.69928 17.3244 7.01184 17.0118C7.3244 16.6993 7.5 16.2754 7.5 15.8333Z" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
    label: '仪表盘'
  },
  {
    icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M10 6.66667V10L12.5 12.5M17.5 10C17.5 14.1421 14.1421 17.5 10 17.5C5.85786 17.5 2.5 14.1421 2.5 10C2.5 5.85786 5.85786 2.5 10 2.5C14.1421 2.5 17.5 5.85786 17.5 10Z" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
    label: '历史告警'
  },
  {
    icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8.0525 14.1667H11.9467M10 2.5V3.33333M15.3033 4.69667L14.7142 5.28583M17.5 10H16.6667M3.33333 10H2.5M5.28583 5.28583L4.69667 4.69667M7.05333 12.9467C6.47072 12.3639 6.074 11.6215 5.91331 10.8132C5.75263 10.005 5.83521 9.1673 6.15061 8.40601C6.466 7.64471 7.00006 6.99403 7.68524 6.53624C8.37042 6.07845 9.17596 5.83411 10 5.83411C10.824 5.83411 11.6296 6.07845 12.3148 6.53624C12.9999 6.99403 13.534 7.64471 13.8494 8.40601C14.1648 9.1673 14.2474 10.005 14.0867 10.8132C13.926 11.6215 13.5293 12.3639 12.9467 12.9467L12.49 13.4025C12.2289 13.6636 12.0218 13.9736 11.8806 14.3148C11.7393 14.6559 11.6666 15.0216 11.6667 15.3908V15.8333C11.6667 16.2754 11.4911 16.6993 11.1785 17.0118C10.866 17.3244 10.442 17.5 10 17.5C9.55797 17.5 9.13405 17.3244 8.82149 17.0118C8.50893 16.6993 8.33333 16.2754 8.33333 15.8333V15.3908C8.33333 14.645 8.03667 13.9292 7.51 13.4025L7.05333 12.9467Z" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
    label: 'AI分析中心'
  },
  {
    icon: '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M8.60417 3.5975C8.95917 2.13417 11.0408 2.13417 11.3958 3.5975M17.5 10C17.5 14.1421 14.1421 17.5 10 17.5C5.85786 17.5 2.5 14.1421 2.5 10C2.5 5.85786 5.85786 2.5 10 2.5C14.1421 2.5 17.5 5.85786 17.5 10Z" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
    label: '用户设置'
  }
];

export const Sidebar: React.FC = () => {
  return (
    <nav className="absolute top-0 left-0 p-6 w-64 bg-white border-r border-solid border-r-neutral-200 h-[874px] max-md:relative max-md:p-4 max-md:w-full max-md:h-auto max-sm:px-2 max-sm:py-4">
      <h1 className="mb-8 text-xl font-semibold leading-8 text-black">
        FinTech AI
      </h1>
      <button className="flex justify-center items-center mb-8 w-8 h-8 rounded bg-neutral-100">
        <div
          dangerouslySetInnerHTML={{
            __html:
              '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2.6665 4H13.3332M2.6665 8H13.3332M2.6665 12H13.3332" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>',
          }}
        />
      </button>
      {navItems.map((item, index) => (
        <NavItem key={index} {...item} />
      ))}
    </nav>
  );
};
