// components/ChartSection.tsx
import React, { useMemo } from 'react';
import { Solicitacao } from '../types';

interface ChartSectionProps {
  data: Solicitacao[];
}

export const ChartSection: React.FC<ChartSectionProps> = ({ data }) => {
  const charts = useMemo(() => {
    // Agrupar por setor
    const setorCounts: Record<string, number> = {};
    data.forEach(d => {
      setorCounts[d.Setor] = (setorCounts[d.Setor] || 0) + 1;
    });
    
    // Top 5 motivos
    const motivoCounts: Record<string, number> = {};
    data.forEach(d => {
      motivoCounts[d.Motivo] = (motivoCounts[d.Motivo] || 0) + 1;
    });
    
    // Status
    const statusCounts: Record<string, number> = {};
    data.forEach(d => {
      statusCounts[d.Status] = (statusCounts[d.Status] || 0) + 1;
    });
    
    // Timeline
    const timelineCounts: Record<string, number> = {};
    data.forEach(d => {
      if (d.Inicio) {
        const parts = d.Inicio.split('/');
        if (parts.length === 3) {
          const date = `${parts[2]}-${parts[1]}-${parts[0]}`;
          timelineCounts[date] = (timelineCounts[date] || 0) + 1;
        }
      }
    });
    
    return {
      setores: Object.entries(setorCounts).sort((a, b) => b[1] - a[1]).slice(0, 10),
      motivos: Object.entries(motivoCounts).sort((a, b) => b[1] - a[1]).slice(0, 5),
      status: Object.entries(statusCounts),
      timeline: Object.entries(timelineCounts).sort((a, b) => a[0].localeCompare(b[0]))
    };
  }, [data]);

  return (
    <>
      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ChartContainer title="Volume por Setor">
          <BarChart data={charts.setores} color="#0ea5e9" />
        </ChartContainer>
        <ChartContainer title="Top 5 Motivos">
          <HorizontalBarChart data={charts.motivos} color="#6366f1" />
        </ChartContainer>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <ChartContainer title="Status dos Pedidos" className="lg:col-span-1">
          <DoughnutChart data={charts.status} />
        </ChartContainer>
        <ChartContainer title="Solicitações por Dia (Início)" className="lg:col-span-2">
          <LineChart data={charts.timeline} />
        </ChartContainer>
      </div>
    </>
  );
};

interface ChartContainerProps {
  title: string;
  children: React.ReactNode;
  className?: string;
}

const ChartContainer: React.FC<ChartContainerProps> = ({ title, children, className = '' }) => (
  <div className={`bg-slate-800 p-4 rounded-xl border border-gray-800 ${className}`}>
    <h3 className="text-base font-semibold mb-3 text-gray-200">{title}</h3>
    <div className="h-48 overflow-hidden">{children}</div>
  </div>
);

// Charts responsivos
const BarChart: React.FC<{ data: [string, number][]; color: string }> = ({ data, color }) => (
  <div className="flex items-end justify-around h-full gap-1 px-2">
    {data.slice(0, 8).map(([label, value], i) => (
      <div key={i} className="flex flex-col items-center gap-1 flex-1 min-w-0">
        <div 
          className="w-full max-w-[30px] rounded-t" 
          style={{ 
            height: `${Math.max((value / Math.max(...data.map(d => d[1]))) * 70, 4)}%`,
            backgroundColor: color,
            minHeight: '4px'
          }}
        />
        <span className="text-[10px] text-gray-400 truncate w-full text-center leading-tight">{label.slice(0, 8)}</span>
      </div>
    ))}
  </div>
);

const HorizontalBarChart: React.FC<{ data: [string, number][]; color: string }> = ({ data, color }) => (
  <div className="flex flex-col justify-center h-full gap-3 py-2">
    {data.slice(0, 5).map(([label, value], i) => (
      <div key={i} className="flex items-center gap-3">
        <span className="text-xs text-gray-400 w-20 truncate">{label.slice(0, 15)}</span>
        <div className="flex-1 bg-slate-700 rounded-full h-3 overflow-hidden">
          <div 
            className="h-full rounded-full transition-all"
            style={{ 
              width: `${Math.max((value / Math.max(...data.map(d => d[1]))) * 100, 5)}%`,
              backgroundColor: color
            }}
          />
        </div>
        <span className="text-xs text-gray-300 w-6 text-right">{value}</span>
      </div>
    ))}
  </div>
);

const DoughnutChart: React.FC<{ data: [string, number][] }> = ({ data }) => {
  const colors = ['#eab308', '#22c55e', '#ef4444', '#3b82f6', '#a855f7'];
  const total = data.reduce((sum, [, val]) => sum + val, 0);
  
  return (
    <div className="flex flex-col items-center h-full justify-center">
      <div className="relative w-28 h-28">
        <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-90">
          {data.reduce((acc, [, value], i) => {
            const prevOffset = acc.offset;
            const percentage = (value / total) * 100;
            acc.offset += percentage;
            
            acc.elements.push(
              <circle
                key={i}
                cx="50"
                cy="50"
                r="35"
                fill="none"
                stroke={colors[i % colors.length]}
                strokeWidth="15"
                strokeDasharray={`${percentage} ${100 - percentage}`}
                strokeDashoffset={-prevOffset}
              />
            );
            return acc;
          }, { elements: [] as React.ReactNode[], offset: 0 }).elements}
        </svg>
      </div>
      <div className="flex flex-wrap justify-center gap-2 mt-3 max-h-16 overflow-y-auto">
        {data.slice(0, 4).map(([label, value], i) => (
          <div key={i} className="flex items-center gap-1">
            <div 
              className="w-2 h-2 rounded-full" 
              style={{ backgroundColor: colors[i % colors.length] }}
            />
            <span className="text-xs text-gray-400">{label} ({value})</span>
          </div>
        ))}
      </div>
    </div>
  );
};

const LineChart: React.FC<{ data: [string, number][] }> = ({ data }) => {
  const max = Math.max(...data.map(d => d[1]));
  const points = data.map(([, value], i) => ({
    x: (i / (data.length - 1 || 1)) * 100,
    y: 100 - (value / max) * 70
  }));
  
  const pathD = points.length > 0 
    ? `M ${points.map(p => `${p.x},${p.y}`).join(' L ')}`
    : '';
  
  return (
    <div className="relative h-full w-full">
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="w-full h-full">
        <defs>
          <linearGradient id="lineGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#10b981" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
          </linearGradient>
        </defs>
        {pathD && (
          <>
            <path
              d={`${pathD} L 100,100 L 0,100 Z`}
              fill="url(#lineGradient)"
            />
            <path
              d={pathD}
              fill="none"
              stroke="#10b981"
              strokeWidth="1.5"
            />
          </>
        )}
      </svg>
      <div className="absolute bottom-0 left-0 right-0 flex justify-between text-[10px] text-gray-500 px-2">
        {data.slice(0, 6).map(([date], i) => (
          <span key={i}>{date.split('-').reverse().join('/')}</span>
        ))}
      </div>
    </div>
  );
};
