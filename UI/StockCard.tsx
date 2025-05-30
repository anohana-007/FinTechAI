import React from 'react';
import { StockData } from './types';

interface StockCardProps extends StockData {}

export const StockCard: React.FC<StockCardProps> = ({
  name,
  code,
  price,
  change,
  upperLimit,
  lowerLimit
}) => {
  return (
    <article className="relative px-4 py-5 mb-4 rounded-lg border border-solid bg-neutral-100 border-neutral-200 h-[167px] w-[573px]">
      <div className="absolute left-[17px] top-[19px]">
        <h3 className="mb-2 text-lg font-semibold leading-7 text-black">{name}</h3>
        <p className="mb-3.5 text-sm leading-5 text-zinc-500">{code}</p>
        <p className="text-sm leading-5 text-zinc-500">价格提醒</p>
      </div>
      <div className="absolute text-right right-[17px] top-[17px]">
        <p className="mb-px text-xl font-semibold leading-8 text-black">{price}</p>
        <p className="mb-3.5 text-sm font-medium leading-5">{change}</p>
        <p className="text-sm leading-5 text-zinc-500">
          <span>上限: {upperLimit}</span>
          <span>| 下限: {lowerLimit}</span>
        </p>
      </div>
      <button className="absolute text-sm font-medium leading-5 text-white bg-black rounded-md cursor-pointer bottom-[17px] h-[37px] right-[17px] w-[101px]">
        查看AI分析
      </button>
    </article>
  );
};
