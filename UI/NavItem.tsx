import React from 'react';
import { NavItemData } from './types';

export const NavItem: React.FC<NavItemData> = ({ icon, label }) => {
  return (
    <div className="flex items-center px-3 py-0 mb-2 h-12 rounded-lg cursor-pointer w-[207px] max-sm:justify-center max-sm:w-12">
      <div dangerouslySetInnerHTML={{ __html: icon }} />
      <span className="ml-3 text-base font-medium leading-6 text-zinc-700">
        {label}
      </span>
    </div>
  );
};
