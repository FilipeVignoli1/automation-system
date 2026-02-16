// components/Dashboard.tsx
import React, { useState, useMemo } from 'react';
import { Solicitacao, DashboardData } from '../types';
import { KPICard } from './KPICard';
import { ChartSection } from './ChartSection';
import { DataTable } from './DataTable';
import { SearchBar } from './SearchBar';

interface DashboardProps {
  data: Solicitacao[];
}

export const Dashboard: React.FC<DashboardProps> = ({ data }) => {
  const [searchTerm, setSearchTerm] = useState('');
  
  const dashboardData: DashboardData = useMemo(() => {
    const total = data.length;
    const pendentes = data.filter(d => d.Status?.toUpperCase().includes('PENDENTE')).length;
    const foraDoPrazo = data.filter(d => 
      d.TempoResolucao?.toUpperCase().includes('FORA DE') || 
      d.PrazoSetor?.toUpperCase().includes('FORA DE')
    ).length;
    const setoresAtivos = [...new Set(data.map(d => d.Setor))].length;
    
    return {
      total,
      pendentes,
      foraDoPrazo,
      setoresAtivos,
      solicitacoes: data
    };
  }, [data]);
  
  const filteredData = useMemo(() => {
    if (!searchTerm) return data;
    const term = searchTerm.toLowerCase();
    return data.filter(row => 
      Object.values(row).some(val => String(val).toLowerCase().includes(term))
    );
  }, [data, searchTerm]);

  return (
    <div className="min-h-screen bg-slate-950 text-gray-100">
      {/* Navbar */}
      <nav className="bg-slate-800 border-b border-gray-800 px-6 py-4">
        <div className="flex justify-between items-center max-w-[1600px] mx-auto">
          <div className="flex items-center gap-3">
            <div className="bg-sky-500/20 p-2 rounded-lg">
              <DashboardIcon />
            </div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              Sirius Dashboard
            </h1>
          </div>
          <div className="text-sm text-gray-400">
            Atualizado: {new Date().toLocaleDateString('pt-BR')}
          </div>
        </div>
      </nav>

      <main className="p-6 max-w-[1600px] mx-auto space-y-6">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard 
            title="Total de Solicitações" 
            value={dashboardData.total} 
            color="primary"
          />
          <KPICard 
            title="Pendentes" 
            value={dashboardData.pendentes}
            percentage={(dashboardData.pendentes / dashboardData.total) * 100}
            color="warning"
          />
          <KPICard 
            title="Fora do Prazo" 
            value={dashboardData.foraDoPrazo}
            percentage={(dashboardData.foraDoPrazo / dashboardData.total) * 100}
            color="danger"
          />
          <KPICard 
            title="Setores Ativos" 
            value={dashboardData.setoresAtivos}
            color="success"
          />
        </div>

        {/* Charts */}
        <ChartSection data={data} />

        {/* Data Table */}
        <div className="bg-slate-800 rounded-xl border border-gray-800 overflow-hidden">
          <div className="p-6 border-b border-gray-800">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-200">Detalhamento</h3>
              <SearchBar value={searchTerm} onChange={setSearchTerm} />
            </div>
          </div>
          <DataTable data={filteredData} />
        </div>
      </main>
    </div>
  );
};

const DashboardIcon: React.FC = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-sky-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z" />
  </svg>
);
