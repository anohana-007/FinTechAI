import React from 'react';
import { AnalysisSectionData } from '../types/types';

export const AnalysisSection: React.FC<AnalysisSectionData> = ({
  title,
  content,
  icon
}) => {
  return (
    <section className="pl-5 mb-4 border-l-4 border-solid border-l-black w-[246px]">
      <div className="flex items-center mb-2.5">
        <div dangerouslySetInnerHTML={{ __html: icon }} />
        <h3 className="text-base font-semibold leading-6 text-black">{title}</h3>
      </div>
      <p className="text-sm leading-5 text-zinc-500">{content}</p>
    </section>
  );
}; 