import React from 'react';
import { NavItemData } from '../types/types';

interface NavItemProps extends NavItemData {
  isActive?: boolean;
  onClick?: () => void;
}

export const NavItem: React.FC<NavItemProps> = ({ icon, label, isActive = false, onClick }) => {
  return (
    <div 
      className={`flex items-center px-3 py-0 mb-2 h-12 rounded-lg cursor-pointer w-[207px] max-sm:justify-center max-sm:w-12 transition-colors ${
        isActive 
          ? 'bg-blue-100 text-blue-700' 
          : 'hover:bg-gray-100'
      }`}
      onClick={onClick}
    >
      <div dangerouslySetInnerHTML={{ __html: icon }} />
      <span className={`ml-3 text-base font-medium leading-6 ${
        isActive ? 'text-blue-700' : 'text-zinc-700'
      }`}>
        {label}
      </span>
    </div>
  );
}; 