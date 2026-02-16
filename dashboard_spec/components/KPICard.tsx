// components/KPICard.tsx
import React from 'react';

interface KPICardProps {
  title: string;
  value: number;
  percentage?: number;
  color: 'primary' | 'warning' | 'danger' | 'success';
}

export const KPICard: React.FC<KPICardProps> = ({ title, value, percentage, color }) => {
  const colorClasses = {
    primary: 'border-gray-800 hover:border-sky-500/50',
    warning: 'border-gray-800 hover:border-yellow-500/50',
    danger: 'border-gray-800 hover:border-red-500/50',
    success: 'border-gray-800 hover:border-green-500/50'
  };
  
  const valueClasses = {
    primary: 'text-white',
    warning: 'text-yellow-400',
    danger: 'text-red-400',
    success: 'text-green-400'
  };

  return (
    <div className={`bg-slate-800 p-4 rounded-xl border transition duration-300 ${colorClasses[color]}`}>
      <h3 className="text-gray-400 text-sm font-medium">{title}</h3>
      <div className="flex items-end gap-2">
        <p className={`text-3xl font-bold mt-2 ${valueClasses[color]}`}>{value}</p>
        {percentage !== undefined && (
          <span className="text-sm text-gray-500 mb-1">({percentage.toFixed(1)}%)</span>
        )}
      </div>
    </div>
  );
};
