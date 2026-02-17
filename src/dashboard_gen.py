import csv
import json
import glob
import os
from pathlib import Path
from src.utils import setup_logging
import config.settings as settings

logger = setup_logging()


def generate_dashboard():
    """Gera dashboard HTML atualizado a partir do arquivo CSV mais recente."""
    try:
        logger.info("Iniciando geração do dashboard...")

        # 1. Encontrar o arquivo CSV mais recente e relevante
        data_dir = Path(settings.DATA_DIR)
        csv_files = list(data_dir.glob("tabela_*_p*_t*.csv"))

        if not csv_files:
            logger.error("Nenhum arquivo CSV de tabela encontrado em 'data/'.")
            return False

        csv_files = [f for f in csv_files if f.stat().st_size > 100]

        if not csv_files:
            logger.error("Nenhum arquivo CSV com dados encontrado.")
            return False

        painel_files = [f for f in csv_files if "_p2_" in f.name]

        if painel_files:
            latest_csv = max(painel_files, key=os.path.getmtime)
        else:
            latest_csv = max(csv_files, key=lambda f: f.stat().st_size)

        logger.info(f"Usando arquivo CSV: {latest_csv.name}")

        # 2. Ler e limpar dados
        data_rows = []
        headers = [
            "Matricula",
            "Nome",
            "Ficha",
            "Prioridade",
            "FollowUp",
            "Setor",
            "Status",
            "Usuario",
            "Macro",
            "Ocorrencia",
            "Motivo",
            "SubMotivo",
            "Inicio",
            "TempoResolucao",
            "PrazoSetor",
            "Conclusao",
        ]

        with open(latest_csv, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 10:
                    while len(row) < len(headers):
                        row.append("")

                    row_dict = {headers[i]: row[i].strip() for i in range(len(headers))}

                    val_matricula = row_dict["Matricula"].upper()
                    # Skip header rows and the "megarow" produced by malformed CSV blocks
                    if (
                        val_matricula in ["TODOS", "MATRICULA"]
                        or "\n" in row_dict["Matricula"]
                        or val_matricula.startswith("MATRICULA")
                    ):
                        continue

                    data_rows.append(row_dict)

        logger.info(f"Processadas {len(data_rows)} linhas de dados.")

        if not data_rows:
            logger.warning("Nenhum dado válido encontrado no CSV.")
            return False

        # 3. Gerar dashboard HTML atualizado
        generate_updated_dashboard_html(data_rows)

        logger.info(f"Dashboard gerado com sucesso!")
        return True

    except Exception as e:
        logger.error(f"Erro ao gerar dashboard: {e}")
        return False


def generate_react_typescript_files(data):
    """Gera componentes React em TypeScript."""

    spec_dir = Path("dashboard_spec")
    spec_dir.mkdir(exist_ok=True)

    # Types
    types_content = """// types/index.ts
export interface Solicitacao {
  Matricula: string;
  Nome: string;
  Ficha: string;
  Prioridade: string;
  FollowUp: string;
  Setor: string;
  Status: 'PENDENTE' | 'CONCLUIDO' | 'EM_ANDAMENTO' | 'CANCELADO';
  Usuario: string;
  Macro: string;
  Ocorrencia: string;
  Motivo: string;
  SubMotivo: string;
  Inicio: string;
  TempoResolucao: string;
  PrazoSetor: string;
  Conclusao: string;
}

export interface DashboardData {
  total: number;
  pendentes: number;
  foraDoPrazo: number;
  setoresAtivos: number;
  solicitacoes: Solicitacao[];
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string;
  }[];
}
"""

    # Dashboard Component
    dashboard_component = """// components/Dashboard.tsx
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
"""

    # KPICard Component
    kpi_card_component = """// components/KPICard.tsx
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
"""

    # ChartSection Component
    chart_section_component = """// components/ChartSection.tsx
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
"""

    # DataTable Component
    data_table_component = """// components/DataTable.tsx
import React from 'react';
import { Solicitacao } from '../types';

interface DataTableProps {
  data: Solicitacao[];
}

export const DataTable: React.FC<DataTableProps> = ({ data }) => {
  const getStatusColor = (status: string): string => {
    if (status?.toUpperCase().includes('PENDENTE')) return 'text-yellow-400';
    if (status?.toUpperCase().includes('CONCLUIDO')) return 'text-green-400';
    if (status?.toUpperCase().includes('CANCELADO')) return 'text-red-400';
    return 'text-gray-400';
  };
  
  const getPrazoClass = (prazo: string): string => {
    if (prazo?.toUpperCase().includes('FORA DE')) {
      return 'bg-red-500/10 text-red-500 border border-red-500/20';
    }
    return 'bg-slate-700 text-gray-400';
  };

  return (
    <>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-gray-400">
          <thead className="bg-slate-700/50 text-gray-200 uppercase font-medium text-xs">
            <tr>
              <th className="px-6 py-3">Matrícula</th>
              <th className="px-6 py-3">Nome</th>
              <th className="px-6 py-3">Setor</th>
              <th className="px-6 py-3">Status</th>
              <th className="px-6 py-3">Ocorrência</th>
              <th className="px-6 py-3">Prazo</th>
              <th className="px-6 py-3">Início</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {data.slice(0, 100).map((row, i) => (
              <tr key={i} className="hover:bg-slate-700/50 transition duration-150">
                <td className="px-6 py-4 font-medium text-gray-200">{row.Matricula}</td>
                <td className="px-6 py-4">{row.Nome}</td>
                <td className="px-6 py-4">{row.Setor}</td>
                <td className={`px-6 py-4 ${getStatusColor(row.Status)}`}>{row.Status}</td>
                <td className="px-6 py-4">{row.Ocorrencia}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded text-xs ${getPrazoClass(row.TempoResolucao)}`}>
                    {row.TempoResolucao}
                  </span>
                </td>
                <td className="px-6 py-4">{row.Inicio}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="p-4 border-t border-gray-800 text-center text-xs text-gray-500">
        Mostrando {Math.min(data.length, 100)} de {data.length} registros
      </div>
    </>
  );
};
"""

    # SearchBar Component
    search_bar_component = """// components/SearchBar.tsx
import React from 'react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({ value, onChange }) => {
  return (
    <div className="relative">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Buscar..."
        className="bg-slate-900 border border-gray-700 rounded-lg px-4 py-2 pl-10 text-sm focus:outline-none focus:border-sky-500 text-gray-300 w-64 transition-colors"
      />
      <svg
        className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 w-4 h-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
        />
      </svg>
    </div>
  );
};
"""

    # App Entry Point
    app_content = """// App.tsx
import React from 'react';
import { Dashboard } from '../components/Dashboard';
import rawData from '../data/solicitacoes.json';

const App: React.FC = () => {
  return <Dashboard data={rawData} />;
};

export default App;
"""

    # Package.json
    package_json = """{
  "name": "sirius-dashboard",
  "version": "1.0.0",
  "description": "Dashboard Sirius - React + TypeScript",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@typescript-eslint/eslint-plugin": "^6.14.0",
    "@typescript-eslint/parser": "^6.14.0",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.55.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.2.2",
    "vite": "^5.0.8"
  }
}"""

    # tsconfig.json
    tsconfig_content = """{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}"""

    # tailwind.config.js
    tailwind_config = """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#0ea5e9',
        secondary: '#6366f1',
        dark: '#0f172a',
        darker: '#020617',
        card: '#1e293b'
      }
    },
  },
  plugins: [],
}"""

    # Additional config files
    index_html = """<!DOCTYPE html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sirius Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>"""

    main_tsx = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)"""

    index_css = """@tailwind base;
@tailwind components;
@tailwind utilities;

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', sans-serif;
  background-color: #020617;
  color: #f8fafc;
}

#root {
  min-height: 100vh;
}"""

    vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true
  }
})"""

    postcss_config = """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}"""

    tsconfig_node = """{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}"""

    vite_env = """/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}"""

    # Save files
    (spec_dir / "types").mkdir(exist_ok=True)
    (spec_dir / "components").mkdir(exist_ok=True)
    (spec_dir / "data").mkdir(exist_ok=True)
    (spec_dir / "src").mkdir(exist_ok=True)

    with open(spec_dir / "types" / "index.ts", "w", encoding="utf-8") as f:
        f.write(types_content)

    with open(spec_dir / "components" / "Dashboard.tsx", "w", encoding="utf-8") as f:
        f.write(dashboard_component)

    with open(spec_dir / "components" / "KPICard.tsx", "w", encoding="utf-8") as f:
        f.write(kpi_card_component)

    with open(spec_dir / "components" / "ChartSection.tsx", "w", encoding="utf-8") as f:
        f.write(chart_section_component)

    with open(spec_dir / "components" / "DataTable.tsx", "w", encoding="utf-8") as f:
        f.write(data_table_component)

    with open(spec_dir / "components" / "SearchBar.tsx", "w", encoding="utf-8") as f:
        f.write(search_bar_component)

    with open(spec_dir / "src" / "App.tsx", "w", encoding="utf-8") as f:
        f.write(app_content)

    with open(spec_dir / "src" / "main.tsx", "w", encoding="utf-8") as f:
        f.write(main_tsx)

    with open(spec_dir / "src" / "index.css", "w", encoding="utf-8") as f:
        f.write(index_css)

    with open(spec_dir / "src" / "vite-env.d.ts", "w", encoding="utf-8") as f:
        f.write(vite_env)

    with open(spec_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    with open(spec_dir / "package.json", "w", encoding="utf-8") as f:
        f.write(package_json)

    with open(spec_dir / "tsconfig.json", "w", encoding="utf-8") as f:
        f.write(tsconfig_content)

    with open(spec_dir / "tsconfig.node.json", "w", encoding="utf-8") as f:
        f.write(tsconfig_node)

    with open(spec_dir / "tailwind.config.js", "w", encoding="utf-8") as f:
        f.write(tailwind_config)

    with open(spec_dir / "postcss.config.js", "w", encoding="utf-8") as f:
        f.write(postcss_config)

    with open(spec_dir / "vite.config.ts", "w", encoding="utf-8") as f:
        f.write(vite_config)

    # Save data
    with open(spec_dir / "data" / "solicitacoes.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # README
    readme_content = """# Sirius Dashboard - React + TypeScript

Dashboard gerado automaticamente a partir dos dados do Sirius.

## 🚀 Como executar

### 1. Instale as dependências
```bash
npm install
```

### 2. Inicie o servidor de desenvolvimento
```bash
npm run dev
```

### 3. Acesse no navegador
O navegador abrirá automaticamente em: `http://localhost:5173`

## 📁 Estrutura do projeto

```
dashboard_spec/
├── src/
│   ├── App.tsx           # Componente principal
│   ├── main.tsx          # Ponto de entrada
│   ├── index.css         # Estilos globais
│   └── vite-env.d.ts     # Tipos do Vite
├── components/
│   ├── Dashboard.tsx     # Dashboard completo
│   ├── KPICard.tsx       # Cards de KPI
│   ├── ChartSection.tsx  # Seção de gráficos
│   ├── DataTable.tsx     # Tabela de dados
│   └── SearchBar.tsx     # Barra de pesquisa
├── types/
│   └── index.ts          # Tipos TypeScript
├── data/
│   └── solicitacoes.json # Dados do Sirius
├── index.html            # HTML principal
├── package.json          # Dependências
├── tsconfig.json         # Config TypeScript
├── tailwind.config.js    # Config Tailwind
└── vite.config.ts        # Config Vite
```

## 🛠️ Comandos disponíveis

- `npm run dev` - Inicia servidor de desenvolvimento
- `npm run build` - Gera build de produção
- `npm run preview` - Visualiza build de produção
- `npm run typecheck` - Verifica tipos TypeScript

## 📝 Notas

- O projeto usa **React 18** com **TypeScript**
- Estilização com **Tailwind CSS**
- Layout em **Dark Mode** (modo escuro)
- Dados atualizados automaticamente via `main.py --dashboard`
"""

    with open(spec_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)


def generate_figma_spec(data):
    """Gera especificação para design no Figma."""

    spec_dir = Path("dashboard_spec")
    from datetime import datetime

    # Calcular estatísticas
    total = len(data)
    pendentes = len([d for d in data if "PENDENTE" in d.get("Status", "").upper()])
    fora_prazo = len(
        [
            d
            for d in data
            if "FORA DE"
            in (d.get("TempoResolucao", "") + d.get("PrazoSetor", "")).upper()
        ]
    )
    setores = len(set(d.get("Setor", "") for d in data))

    # Agrupar dados
    setor_counts = dict()
    for d in data:
        setor_counts[d.get("Setor", "N/A")] = (
            setor_counts.get(d.get("Setor", "N/A"), 0) + 1
        )

    motivo_counts = dict()
    for d in data:
        motivo_counts[d.get("Motivo", "N/A")] = (
            motivo_counts.get(d.get("Motivo", "N/A"), 0) + 1
        )

    status_counts = dict()
    for d in data:
        status_counts[d.get("Status", "N/A")] = (
            status_counts.get(d.get("Status", "N/A"), 0) + 1
        )

    figma_spec = "# Especificação Figma - Sirius Dashboard\n\n"
    figma_spec += "## 📐 Layout System\n\n"
    figma_spec += "### Grid\n"
    figma_spec += "- **Container máximo**: 1600px\n"
    figma_spec += "- **Padding**: 24px (p-6)\n"
    figma_spec += "- **Gap entre cards**: 16px (gap-4)\n"
    figma_spec += "- **Grid responsivo**: \n"
    figma_spec += "  - Mobile: 1 coluna\n"
    figma_spec += "  - Tablet: 2 colunas\n"
    figma_spec += "  - Desktop: 4 colunas (KPIs), 2 colunas (charts)\n\n"

    figma_spec += "### Cores (Dark Mode)\n\n"
    figma_spec += "#### Backgrounds\n"
    figma_spec += "- **Primary BG**: `#0f172a` (slate-900)\n"
    figma_spec += "- **Card BG**: `#1e293b` (slate-800)\n"
    figma_spec += "- **Darker BG**: `#020617` (slate-950)\n"
    figma_spec += "- **Input BG**: `#0f172a` (slate-900)\n\n"

    figma_spec += "#### Textos\n"
    figma_spec += "- **Heading**: `#f8fafc` (white)\n"
    figma_spec += "- **Body**: `#94a3b8` (gray-400)\n"
    figma_spec += "- **Muted**: `#64748b` (gray-500)\n\n"

    figma_spec += "#### Cores de Status\n"
    figma_spec += "- **Primary**: `#0ea5e9` (sky-500)\n"
    figma_spec += "- **Success**: `#22c55e` (green-500)\n"
    figma_spec += "- **Warning**: `#eab308` (yellow-500)\n"
    figma_spec += "- **Danger**: `#ef4444` (red-500)\n"
    figma_spec += "- **Secondary**: `#6366f1` (indigo-500)\n\n"

    figma_spec += "#### Bordas\n"
    figma_spec += "- **Default**: `#1e293b` (gray-800)\n"
    figma_spec += "- **Hover**: Com 50% de opacidade da cor primária\n\n"

    figma_spec += "## 🧩 Componentes\n\n"
    figma_spec += "### 1. Navbar\n"
    figma_spec += "- **Altura**: 64px\n"
    figma_spec += "- **Background**: `#1e293b`\n"
    figma_spec += "- **Border-bottom**: 1px solid `#1e293b`\n"
    figma_spec += "- **Padding**: 24px horizontal, 16px vertical\n"
    figma_spec += "- **Shadow**: subtle\n\n"

    figma_spec += "### 2. KPI Card\n"
    figma_spec += "- **Background**: `#1e293b`\n"
    figma_spec += "- **Border**: 1px solid `#1e293b`\n"
    figma_spec += "- **Border-radius**: 12px\n"
    figma_spec += "- **Padding**: 16px\n"
    figma_spec += "- **Hover**: Border color muda para cor do status\n"
    figma_spec += "- **Título**: 14px, medium, gray-400\n"
    figma_spec += "- **Valor**: 30px, bold, cor do status\n\n"

    figma_spec += "**Estados:**\n"
    figma_spec += "- Primary: border sky-500/50, text white\n"
    figma_spec += "- Warning: border yellow-500/50, text yellow-400\n"
    figma_spec += "- Danger: border red-500/50, text red-400\n"
    figma_spec += "- Success: border green-500/50, text green-400\n\n"

    figma_spec += "### 3. Chart Card\n"
    figma_spec += "- **Background**: `#1e293b`\n"
    figma_spec += "- **Border**: 1px solid `#1e293b`\n"
    figma_spec += "- **Border-radius**: 12px\n"
    figma_spec += "- **Padding**: 24px\n"
    figma_spec += "- **Título**: 18px, semibold, gray-200\n"
    figma_spec += "- **Chart height**: 256px\n\n"

    figma_spec += "### 4. Data Table\n"
    figma_spec += "- **Background**: `#1e293b`\n"
    figma_spec += "- **Border**: 1px solid `#1e293b`\n"
    figma_spec += "- **Border-radius**: 12px\n"
    figma_spec += "- **Header**: \n"
    figma_spec += "  - Background: `#334155` (slate-700/50)\n"
    figma_spec += "  - Text: 12px, uppercase, gray-200\n"
    figma_spec += "  - Padding: 12px 24px\n"
    figma_spec += "- **Row**:\n"
    figma_spec += "  - Border-bottom: 1px solid `#1e293b`\n"
    figma_spec += "  - Hover: bg slate-700/50\n"
    figma_spec += "  - Padding: 16px 24px\n"
    figma_spec += "  - Text: 14px, gray-400\n\n"

    figma_spec += "### 5. Search Input\n"
    figma_spec += "- **Background**: `#0f172a`\n"
    figma_spec += "- **Border**: 1px solid `#374151`\n"
    figma_spec += "- **Border-radius**: 8px\n"
    figma_spec += "- **Padding**: 8px 16px 8px 40px (com ícone)\n"
    figma_spec += "- **Width**: 256px\n"
    figma_spec += "- **Placeholder**: gray-500\n"
    figma_spec += "- **Focus**: border sky-500\n\n"

    figma_spec += "### 6. Status Badge\n"
    figma_spec += "- **Prazo OK**: bg slate-700, text gray-400\n"
    figma_spec += (
        "- **Fora do Prazo**: bg red-500/10, text red-500, border red-500/20\n"
    )
    figma_spec += "- **Border-radius**: 4px\n"
    figma_spec += "- **Padding**: 4px 8px\n"
    figma_spec += "- **Font**: 12px\n\n"

    figma_spec += "## 📊 Dados para Prototipagem\n\n"
    figma_spec += f"**Total de Solicitações**: {total}\n"
    figma_spec += f"**Pendentes**: {pendentes} ({(pendentes / total * 100):.1f}%)\n"
    figma_spec += (
        f"**Fora do Prazo**: {fora_prazo} ({(fora_prazo / total * 100):.1f}%)\n"
    )
    figma_spec += f"**Setores Ativos**: {setores}\n\n"

    figma_spec += "### Gráficos\n\n"
    figma_spec += "**Volume por Setor (Top 10):**\n"
    for setor, count in sorted(setor_counts.items(), key=lambda x: x[1], reverse=True)[
        :10
    ]:
        figma_spec += f"- {setor}: {count}\n"

    figma_spec += "\n**Top 5 Motivos:**\n"
    for motivo, count in sorted(
        motivo_counts.items(), key=lambda x: x[1], reverse=True
    )[:5]:
        figma_spec += f"- {motivo}: {count}\n"

    figma_spec += "\n**Status:**\n"
    for status, count in sorted(
        status_counts.items(), key=lambda x: x[1], reverse=True
    ):
        figma_spec += f"- {status}: {count}\n"

    figma_spec += "\n## 📝 Anotações de Design\n\n"
    figma_spec += "### Tipografia\n"
    figma_spec += "- **Fonte**: Inter, sans-serif\n"
    figma_spec += "- **Headings**: Font-bold\n"
    figma_spec += "- **Body**: Font-normal\n\n"

    figma_spec += "### Espaçamento\n"
    figma_spec += "- **xs**: 4px\n"
    figma_spec += "- **sm**: 8px\n"
    figma_spec += "- **md**: 16px\n"
    figma_spec += "- **lg**: 24px\n"
    figma_spec += "- **xl**: 32px\n\n"

    figma_spec += "### Border Radius\n"
    figma_spec += "- **sm**: 4px (badges)\n"
    figma_spec += "- **md**: 8px (inputs)\n"
    figma_spec += "- **lg**: 12px (cards)\n\n"

    figma_spec += "### Sombras\n"
    figma_spec += "- **Cards**: Subtle shadow on hover\n"
    figma_spec += "- **Navbar**: shadow-sm\n\n"

    figma_spec += "## 🎨 Protótipo Visual\n\n"
    figma_spec += "### Estrutura da Página\n"
    figma_spec += "```\n"
    figma_spec += "┌─────────────────────────────────────────────────────────────┐\n"
    figma_spec += "│  [Logo] Sirius Dashboard                    Atualizado: Hoje│\n"
    figma_spec += "├─────────────────────────────────────────────────────────────┤\n"
    figma_spec += f"│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │\n"
    figma_spec += f"│  │ Total    │ │Pendentes │ │Fora Prazo│ │ Setores  │       │\n"
    figma_spec += f"│  │   {total:<4}   │ │  {pendentes:<4}    │ │   {fora_prazo:<4}    │ │   {setores:<4}    │       │\n"
    figma_spec += "│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │\n"
    figma_spec += "│                                                             │\n"
    figma_spec += "│  ┌──────────────────────────┐ ┌──────────────────────────┐  │\n"
    figma_spec += "│  │ Volume por Setor         │ │ Top 5 Motivos            │  │\n"
    figma_spec += "│  │ [Bar Chart]              │ │ [Horizontal Bar]         │  │\n"
    figma_spec += "│  └──────────────────────────┘ └──────────────────────────┘  │\n"
    figma_spec += "│                                                             │\n"
    figma_spec += "│  ┌──────────────────┐ ┌───────────────────────────────────┐ │\n"
    figma_spec += "│  │ Status           │ │ Timeline                          │ │\n"
    figma_spec += "│  │ [Doughnut]       │ │ [Line Chart]                      │ │\n"
    figma_spec += "│  └──────────────────┘ └───────────────────────────────────┘ │\n"
    figma_spec += "│                                                             │\n"
    figma_spec += "│  ┌─────────────────────────────────────────────────────────┐│\n"
    figma_spec += "│  │ Detalhamento                              [Buscar...]   ││\n"
    figma_spec += "│  │ ┌─────────────────────────────────────────────────────┐ ││\n"
    figma_spec += "│  │ │ Matrícula │ Nome │ Setor │ Status │ ...            │ ││\n"
    figma_spec += "│  │ └─────────────────────────────────────────────────────┘ ││\n"
    figma_spec += "│  └─────────────────────────────────────────────────────────┘│\n"
    figma_spec += "└─────────────────────────────────────────────────────────────┘\n"
    figma_spec += "```\n\n"
    figma_spec += "---\n"
    figma_spec += f"**Gerado em**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

    with open(spec_dir / "FIGMA_SPEC.md", "w", encoding="utf-8") as f:
        f.write(figma_spec)


def generate_updated_dashboard_html(data):
    """Gera o dashboard HTML atualizado com todos os dados mais recentes."""
    try:
        from datetime import datetime
        import shutil

        # Verificar se existe o dashboard.html atualizado na raiz
        root_dashboard = Path("dashboard.html")
        output_dashboard = Path("dashboard.html")

        if not root_dashboard.exists():
            logger.warning(
                "dashboard.html não encontrado na raiz. Usando template padrão."
            )
            generate_simple_html(data)
            return

        # Ler o dashboard.html existente
        with open(root_dashboard, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Preparar os dados para injeção no JavaScript
        data_json = json.dumps(data, ensure_ascii=False, indent=2)
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Substituir os dados no HTML
        # Procura por: const rawData = [...]; ou const rawData = REPLACE_DATA_HERE;
        import re

        # Substituição dos dados
        if "REPLACE_DATA_HERE" in html_content:
            html_content = html_content.replace("REPLACE_DATA_HERE", data_json)
        elif "const rawData = [" in html_content:
            # Procura pelo padrão const rawData = [...];
            pattern = r"const rawData = \[.*?\];"
            html_content = re.sub(
                pattern, f"const rawData = {data_json};", html_content, flags=re.DOTALL
            )
        else:
            # Se não encontrar o padrão, insere após o <script>
            script_tag = "<script>"
            data_script = f'<script>\n        const rawData = {data_json};\n        const lastUpdate = "{timestamp}";'
            html_content = html_content.replace(script_tag, data_script, 1)

        # Substituição do timestamp
        if "REPLACE_TIME_HERE" in html_content:
            html_content = html_content.replace("REPLACE_TIME_HERE", timestamp)
        elif 'const lastUpdate = "' in html_content:
            pattern = r'const lastUpdate = "[^"]*"'
            html_content = re.sub(
                pattern, f'const lastUpdate = "{timestamp}"', html_content
            )

        # Salvar o arquivo atualizado
        with open(output_dashboard, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Dashboard HTML atualizado: {output_dashboard}")

        # Também gerar especificação React para referência
        generate_react_typescript_files(data)
        generate_figma_spec(data)

    except Exception as e:
        logger.error(f"Erro ao gerar dashboard HTML atualizado: {e}")
        # Fallback para o método simples
        generate_simple_html(data)


def generate_simple_html(data):
    """Gera um arquivo HTML único e auto-contido para visualização direta."""
    try:
        from datetime import datetime

        html_template = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sirius Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#3b82f6',
                        primaryHover: '#2563eb',
                        success: '#10b981',
                        warning: '#f59e0b',
                        danger: '#ef4444',
                        gray: {
                            50: '#f9fafb',
                            100: '#f3f4f6',
                            200: '#e5e7eb',
                            300: '#d1d5db',
                            400: '#9ca3af',
                            500: '#6b7280',
                            600: '#4b5563',
                            700: '#374151',
                            800: '#1f2937',
                            900: '#111827',
                        }
                    }
                }
            }
        }
    </script>
    <style>
        * { font-family: 'Inter', sans-serif; }
        
        .sidebar {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .sidebar.collapsed {
            width: 70px;
        }
        
        .sidebar.collapsed .nav-text,
        .sidebar.collapsed .filter-section,
        .sidebar.collapsed .logo-text {
            opacity: 0;
            pointer-events: none;
        }
        
        .sidebar.collapsed .nav-item {
            justify-content: center;
            padding: 0.75rem;
        }
        
        .card {
            transition: all 0.2s ease;
        }
        
        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.1);
        }
        
        .kpi-card {
            background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
        }
        
        .chart-container {
            position: relative;
            height: 300px;
        }
        
        .table-row:hover {
            background-color: #f9fafb;
        }
        
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #a1a1a1;
        }
    </style>
</head>
<body class="bg-gray-50 text-gray-800">
    <div class="flex h-screen">
        <!-- Sidebar -->
        <aside id="sidebar" class="sidebar w-64 bg-white border-r border-gray-200 flex flex-col fixed h-full z-30">
            <button id="sidebarToggle" class="absolute -right-3 top-20 bg-primary text-white w-6 h-6 rounded-full flex items-center justify-center shadow-md hover:bg-primaryHover transition z-50">
                <svg id="toggleIcon" xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
            </button>

            <div class="h-16 flex items-center px-6 border-b border-gray-100">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                    </div>
                    <span class="logo-text font-bold text-xl text-gray-900 transition-opacity duration-200">Sirius</span>
                </div>
            </div>

            <nav class="flex-1 overflow-y-auto py-4 px-3">
                <div class="space-y-1">
                    <a href="#overview" class="nav-item flex items-center gap-3 px-3 py-2.5 rounded-lg bg-primary/10 text-primary font-medium transition">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                        </svg>
                        <span class="nav-text whitespace-nowrap transition-opacity duration-200">Dashboard</span>
                    </a>
                    
                    <a href="#analytics" class="nav-item flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z" />
                        </svg>
                        <span class="nav-text whitespace-nowrap transition-opacity duration-200">Analytics</span>
                    </a>
                    
                    <a href="#data" class="nav-item flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span class="nav-text whitespace-nowrap transition-opacity duration-200">Relatórios</span>
                    </a>
                    
                    <a href="#" id="btnResponsaveis" class="nav-item flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                        </svg>
                        <span class="nav-text whitespace-nowrap transition-opacity duration-200">Responsáveis</span>
                    </a>
                </div>

                <div class="filter-section mt-8 px-3">
                    <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Filtros</p>
                    <div class="space-y-3">
                        <div>
                            <label class="text-xs text-gray-500 mb-1.5 block">Setor</label>
                            <select id="filterSetor" class="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20">
                                <option value="">Todos os setores</option>
                            </select>
                        </div>
                        <button id="clearFilter" class="w-full bg-gray-100 hover:bg-gray-200 text-gray-600 text-sm py-2 rounded-lg transition flex items-center justify-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                            <span class="filter-text">Limpar</span>
                        </button>
                    </div>
                </div>
            </nav>

            <div class="p-4 border-t border-gray-100">
                <div class="filter-section text-xs text-gray-400">
                    <p>Última atualização</p>
                    <p id="lastUpdated" class="font-medium text-gray-600 mt-0.5">--</p>
                </div>
            </div>
        </aside>

        <!-- Main Content -->
        <main id="mainContent" class="flex-1 ml-64 transition-all duration-300">
            <!-- Header -->
            <header class="h-16 bg-white border-b border-gray-200 px-8 flex items-center justify-between sticky top-0 z-20">
                <div>
                    <h1 class="text-xl font-semibold text-gray-900">Dashboard</h1>
                    <p class="text-sm text-gray-500">Visão geral das solicitações</p>
                </div>
                <div class="flex items-center gap-4">
                    <div class="relative">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        <input type="text" id="globalSearch" placeholder="Buscar em todo o sistema..." 
                               class="pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20 w-64">
                    </div>
                    <button class="bg-primary hover:bg-primaryHover text-white px-4 py-2 rounded-lg text-sm font-medium transition flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        Exportar
                    </button>
                </div>
            </header>

            <!-- Content -->
            <div class="p-8 space-y-8">
                <!-- KPI Cards -->
                <section id="overview" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div class="card kpi-card p-6 rounded-2xl border border-gray-100 shadow-sm">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm font-medium text-gray-500">Total de Solicitações</p>
                                <p class="text-3xl font-bold text-gray-900 mt-1" id="kpiTotal">0</p>
                            </div>
                            <div class="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                </svg>
                            </div>
                        </div>
                    </div>

                    <div class="card kpi-card p-6 rounded-2xl border border-gray-100 shadow-sm">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm font-medium text-gray-500">Pendentes</p>
                                <div class="flex items-baseline gap-2 mt-1">
                                    <p class="text-3xl font-bold text-warning" id="kpiPending">0</p>
                                    <span class="text-sm text-warning/70" id="kpiPendingPct">0%</span>
                                </div>
                            </div>
                            <div class="w-12 h-12 bg-yellow-50 rounded-xl flex items-center justify-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                        </div>
                    </div>

                    <div class="card kpi-card p-6 rounded-2xl border border-gray-100 shadow-sm">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm font-medium text-gray-500">Fora do Prazo</p>
                                <div class="flex items-baseline gap-2 mt-1">
                                    <p class="text-3xl font-bold text-danger" id="kpiLate">0</p>
                                    <span class="text-sm text-danger/70" id="kpiLatePct">0%</span>
                                </div>
                            </div>
                            <div class="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-danger" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                            </div>
                        </div>
                    </div>

                    <div class="card kpi-card p-6 rounded-2xl border border-gray-100 shadow-sm">
                        <div class="flex items-center justify-between">
                            <div>
                                <p class="text-sm font-medium text-gray-500">Setores Ativos</p>
                                <p class="text-3xl font-bold text-success" id="kpiSectors">0</p>
                            </div>
                            <div class="w-12 h-12 bg-green-50 rounded-xl flex items-center justify-center">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                                </svg>
                            </div>
                        </div>
                    </div>
                </section>

                <!-- Charts Row 1 -->
                <section id="analytics" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div class="card bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
                        <div class="flex items-center justify-between mb-6">
                            <h3 class="text-lg font-semibold text-gray-900">Volume por Setor</h3>
                        </div>
                        <div class="chart-container">
                            <canvas id="chartSector"></canvas>
                        </div>
                    </div>

                    <div class="card bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
                        <div class="flex items-center justify-between mb-6">
                            <h3 class="text-lg font-semibold text-gray-900">Top 5 Motivos</h3>
                        </div>
                        <div class="chart-container">
                            <canvas id="chartMotivo"></canvas>
                        </div>
                    </div>
                </section>

                <!-- Charts Row 2 -->
                <section class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="card bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
                        <h3 class="text-lg font-semibold text-gray-900 mb-6">Status dos Pedidos</h3>
                        <div class="chart-container flex items-center justify-center">
                            <canvas id="chartStatus"></canvas>
                        </div>
                    </div>

                    <div class="card bg-white p-6 rounded-2xl border border-gray-100 shadow-sm lg:col-span-2">
                        <div class="flex items-center justify-between mb-6">
                            <h3 class="text-lg font-semibold text-gray-900">Solicitações por Dia</h3>
                            <div class="flex items-center gap-2">
                                <span class="text-sm text-gray-500">Últimos 30 dias</span>
                            </div>
                        </div>
                        <div class="chart-container">
                            <canvas id="chartTimeline"></canvas>
                        </div>
                    </div>
                </section>

                <!-- Tabela de Ocorrências -->
                <section class="card bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                    <div class="p-6 border-b border-gray-100">
                        <div class="flex items-center justify-between">
                            <div>
                                <h3 class="text-lg font-semibold text-gray-900">Contagem por Ocorrência</h3>
                                <p class="text-sm text-gray-500 mt-1">Análise completa com Prazo e Período</p>
                            </div>
                            <div class="bg-primary/10 px-4 py-2 rounded-lg">
                                <span class="text-sm text-gray-600">Total: </span>
                                <span class="text-lg font-bold text-primary" id="totalOcorrencias">0</span>
                            </div>
                        </div>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-4 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Ocorrência / Motivo / Submotivo</th>
                                    <th class="px-4 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Total</th>
                                    <th class="px-4 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">%</th>
                                    <th class="px-4 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider text-red-600">Fora Prazo</th>
                                    <th class="px-4 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider text-green-600">No Prazo</th>
                                    <th class="px-4 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Mais Antiga</th>
                                    <th class="px-4 py-4 text-center text-xs font-semibold text-gray-500 uppercase tracking-wider">Mais Recente</th>
                                    <th class="px-4 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Distribuição</th>
                                </tr>
                            </thead>
                            <tbody id="ocorrenciaTableBody" class="divide-y divide-gray-100">
                            </tbody>
                        </table>
                    </div>
                </section>

                <!-- Data Table -->
                <section id="data" class="card bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                    <div class="p-6 border-b border-gray-100 flex items-center justify-between">
                        <h3 class="text-lg font-semibold text-gray-900">Detalhamento</h3>
                        <div class="flex items-center gap-3">
                            <span class="text-sm text-gray-500">Mostrando <span id="rowCount" class="font-medium text-gray-900">0</span> de <span id="totalCount" class="font-medium text-gray-900">0</span> registros</span>
                        </div>
                    </div>
                    <div class="overflow-x-auto">
                        <table class="w-full">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Matrícula</th>
                                    <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Nome</th>
                                    <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Setor</th>
                                    <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Status</th>
                                    <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Ocorrência</th>
                                    <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Prazo</th>
                                    <th class="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Início</th>
                                </tr>
                            </thead>
                            <tbody id="tableBody" class="divide-y divide-gray-100">
                            </tbody>
                        </table>
                    </div>
                </section>
            </div>
        </main>
    </div>

    <script>
        const rawData = REPLACE_DATA_HERE;
        const lastUpdate = "REPLACE_TIME_HERE";

        // DOM Elements
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.getElementById('mainContent');
        const sidebarToggle = document.getElementById('sidebarToggle');
        const toggleIcon = document.getElementById('toggleIcon');
        const filterSetor = document.getElementById('filterSetor');
        const clearFilter = document.getElementById('clearFilter');
        const lastUpdated = document.getElementById('lastUpdated');

        // Initialize
        lastUpdated.textContent = lastUpdate;

        // Populate sector filter
        const sectors = [...new Set(rawData.map(d => d.Setor).filter(Boolean))].sort();
        sectors.forEach(sector => {
            const option = document.createElement('option');
            option.value = sector;
            option.textContent = sector;
            filterSetor.appendChild(option);
        });

        // Sidebar toggle
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            if (sidebar.classList.contains('collapsed')) {
                mainContent.style.marginLeft = '70px';
                toggleIcon.style.transform = 'rotate(180deg)';
            } else {
                mainContent.style.marginLeft = '256px';
                toggleIcon.style.transform = 'rotate(0deg)';
            }
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        });

        // Restore sidebar state
        if (localStorage.getItem('sidebarCollapsed') === 'true') {
            sidebar.classList.add('collapsed');
            mainContent.style.marginLeft = '70px';
            toggleIcon.style.transform = 'rotate(180deg)';
        }

        // Filter functionality
        let currentFilter = '';

        function applyFilter() {
            let filtered = rawData;
            if (currentFilter) {
                filtered = rawData.filter(d => d.Setor === currentFilter);
            }
            renderTable(filtered);
        }

        filterSetor.addEventListener('change', (e) => {
            currentFilter = e.target.value;
            applyFilter();
        });

        clearFilter.addEventListener('click', () => {
            currentFilter = '';
            filterSetor.value = '';
            applyFilter();
        });

        // Global search
        document.getElementById('globalSearch').addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const filtered = rawData.filter(row => 
                Object.values(row).some(val => 
                    String(val).toLowerCase().includes(term)
                )
            );
            renderTable(filtered);
        });

        // Calculate KPIs
        const total = rawData.length;
        const pending = rawData.filter(d => d.Status?.toUpperCase().includes('PENDENTE')).length;
        const late = rawData.filter(d => 
            d.TempoResolucao?.toUpperCase().includes('FORA DE') || 
            d.PrazoSetor?.toUpperCase().includes('FORA DE')
        ).length;
        const sectorsCount = [...new Set(rawData.map(d => d.Setor))].length;

        document.getElementById('kpiTotal').textContent = total;
        document.getElementById('kpiPending').textContent = pending;
        document.getElementById('kpiPendingPct').textContent = `${((pending / total) * 100).toFixed(1)}%`;
        document.getElementById('kpiLate').textContent = late;
        document.getElementById('kpiLatePct').textContent = `${((late / total) * 100).toFixed(1)}%`;
        document.getElementById('kpiSectors').textContent = sectorsCount;

        // Chart helpers
        function getCounts(field) {
            const counts = {};
            rawData.forEach(d => {
                const val = d[field] || 'N/A';
                counts[val] = (counts[val] || 0) + 1;
            });
            return Object.entries(counts).sort((a, b) => b[1] - a[1]);
        }

        // Initialize charts
        new Chart(document.getElementById('chartSector'), {
            type: 'bar',
            data: {
                labels: getCounts('Setor').slice(0, 10).map(d => d[0]),
                datasets: [{
                    label: 'Solicitações',
                    data: getCounts('Setor').slice(0, 10).map(d => d[1]),
                    backgroundColor: '#3b82f6',
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#f3f4f6' } },
                    x: { grid: { display: false } }
                }
            }
        });

        new Chart(document.getElementById('chartMotivo'), {
            type: 'bar',
            data: {
                labels: getCounts('Motivo').slice(0, 5).map(d => d[0]),
                datasets: [{
                    label: 'Ocorrências',
                    data: getCounts('Motivo').slice(0, 5).map(d => d[1]),
                    backgroundColor: '#6366f1',
                    borderRadius: 6,
                    borderSkipped: false
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { beginAtZero: true, grid: { color: '#f3f4f6' } },
                    y: { grid: { display: false } }
                }
            }
        });

        new Chart(document.getElementById('chartStatus'), {
            type: 'doughnut',
            data: {
                labels: getCounts('Status').map(d => d[0]),
                datasets: [{
                    data: getCounts('Status').map(d => d[1]),
                    backgroundColor: ['#f59e0b', '#10b981', '#ef4444', '#3b82f6'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: { position: 'bottom', labels: { padding: 20, usePointStyle: true } }
                }
            }
        });

        // Tabela de Ocorrências com hierarquia Ocorrência → Motivo → Submotivo em uma coluna
        const ocorrenciaData = getCounts('Ocorrencia');
        const totalOcorrencias = ocorrenciaData.reduce((sum, [, count]) => sum + count, 0);
        document.getElementById('totalOcorrencias').textContent = totalOcorrencias.toLocaleString('pt-BR');
        
        const ocorrenciaColors = ['bg-blue-500', 'bg-indigo-500', 'bg-violet-500', 'bg-purple-500', 'bg-fuchsia-500', 'bg-pink-500', 'bg-rose-500', 'bg-orange-500', 'bg-yellow-500', 'bg-green-500', 'bg-teal-500', 'bg-cyan-500', 'bg-sky-500', 'bg-blue-600', 'bg-indigo-600'];
        
        const ocorrenciaTbody = document.getElementById('ocorrenciaTableBody');
        const maxOcorrenciaCount = Math.max(...ocorrenciaData.map(d => d[1]));
        
        // Função para converter data DD/MM/YYYY para objeto Date
        function parseDate(dateStr) {
            if (!dateStr) return null;
            const parts = dateStr.split('/');
            if (parts.length !== 3) return null;
            return new Date(parts[2], parts[1] - 1, parts[0]);
        }
        
        // Função para agrupar dados por Ocorrência → Motivo → Submotivo
        function getHierarquiaPorOcorrencia(ocorrencia) {
            const dadosOcorrencia = rawData.filter(d => d.Ocorrencia === ocorrencia);
            const hierarquia = {};
            
            dadosOcorrencia.forEach(d => {
                const motivo = d.Motivo || 'N/A';
                const submotivo = d.SubMotivo || 'N/A';
                
                if (!hierarquia[motivo]) {
                    hierarquia[motivo] = {
                        count: 0,
                        foraPrazo: 0,
                        submotivos: {}
                    };
                }
                
                hierarquia[motivo].count++;
                
                if (d.TempoResolucao?.toUpperCase().includes('FORA DE') || 
                    d.PrazoSetor?.toUpperCase().includes('FORA DE')) {
                    hierarquia[motivo].foraPrazo++;
                }
                
                if (!hierarquia[motivo].submotivos[submotivo]) {
                    hierarquia[motivo].submotivos[submotivo] = {
                        count: 0,
                        foraPrazo: 0,
                        datas: []
                    };
                }
                
                hierarquia[motivo].submotivos[submotivo].count++;
                
                if (d.TempoResolucao?.toUpperCase().includes('FORA DE') || 
                    d.PrazoSetor?.toUpperCase().includes('FORA DE')) {
                    hierarquia[motivo].submotivos[submotivo].foraPrazo++;
                }
                
                const data = parseDate(d.Inicio);
                if (data) {
                    hierarquia[motivo].submotivos[submotivo].datas.push(data);
                }
            });
            
            return Object.entries(hierarquia)
                .sort((a, b) => b[1].count - a[1].count)
                .map(([motivo, dados]) => ({
                    motivo,
                    ...dados,
                    submotivos: Object.entries(dados.submotivos)
                        .sort((a, b) => b[1].count - a[1].count)
                }));
        }
        
        ocorrenciaData.forEach(([ocorrencia, count], index) => {
            const percentual = ((count / totalOcorrencias) * 100).toFixed(1);
            const barWidth = (count / maxOcorrenciaCount) * 100;
            const colorClass = ocorrenciaColors[index % ocorrenciaColors.length];
            
            // Filtrar dados desta ocorrência específica
            const dadosOcorrencia = rawData.filter(d => d.Ocorrencia === ocorrencia);
            
            // Contar fora do prazo
            const foraPrazo = dadosOcorrencia.filter(d => 
                d.TempoResolucao?.toUpperCase().includes('FORA DE') || 
                d.PrazoSetor?.toUpperCase().includes('FORA DE')
            ).length;
            
            const noPrazo = count - foraPrazo;
            const percentualForaPrazo = ((foraPrazo / count) * 100).toFixed(0);
            
            // Encontrar datas de início
            const datasInicio = dadosOcorrencia
                .map(d => parseDate(d.Inicio))
                .filter(d => d !== null)
                .sort((a, b) => a - b);
            
            const dataMaisAntiga = datasInicio.length > 0 
                ? datasInicio[0].toLocaleDateString('pt-BR') 
                : '-';
            const dataMaisRecente = datasInicio.length > 0 
                ? datasInicio[datasInicio.length - 1].toLocaleDateString('pt-BR') 
                : '-';
            
            // Linha principal da Ocorrência
            const trPrincipal = document.createElement('tr');
            trPrincipal.className = 'table-row transition-colors hover:bg-gray-50 bg-gray-50/50';
            trPrincipal.innerHTML = `
                <td class="px-4 py-4">
                    <div class="flex items-center gap-2">
                        <div class="w-3 h-3 rounded-full ${colorClass}"></div>
                        <span class="text-sm font-bold text-gray-900">${ocorrencia}</span>
                        <span class="text-xs text-gray-500 ml-2">(${count} total)</span>
                    </div>
                </td>
                <td class="px-4 py-4 text-center">
                    <span class="text-sm font-bold text-gray-900">${count}</span>
                </td>
                <td class="px-4 py-4 text-center">
                    <span class="text-xs text-gray-600">${percentual}%</span>
                </td>
                <td class="px-4 py-4 text-center">
                    ${foraPrazo > 0 
                        ? `<span class="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">${foraPrazo} <span class="text-red-500">(${percentualForaPrazo}%)</span></span>`
                        : `<span class="text-xs text-gray-400">-</span>`
                    }
                </td>
                <td class="px-4 py-4 text-center">
                    ${noPrazo > 0 
                        ? `<span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">${noPrazo}</span>`
                        : `<span class="text-xs text-gray-400">-</span>`
                    }
                </td>
                <td class="px-4 py-4 text-center">
                    <span class="text-xs text-gray-600">${dataMaisAntiga}</span>
                </td>
                <td class="px-4 py-4 text-center">
                    <span class="text-xs text-gray-600">${dataMaisRecente}</span>
                </td>
                <td class="px-4 py-4">
                    <div class="flex items-center gap-2">
                        <div class="flex-1 bg-gray-200 rounded-full h-2 max-w-[120px]">
                            <div class="${colorClass} h-2 rounded-full transition-all duration-500" style="width: ${barWidth}%"></div>
                        </div>
                    </div>
                </td>
            `;
            ocorrenciaTbody.appendChild(trPrincipal);
            
            // Linhas dos Motivos e Submotivos
            const hierarquia = getHierarquiaPorOcorrencia(ocorrencia);
            hierarquia.forEach((motivoData) => {
                // Linhas dos Submotivos com Motivo + Submotivo combinados
                motivoData.submotivos.forEach(([submotivo, subDados]) => {
                    const subPercentual = ((subDados.count / count) * 100).toFixed(0);
                    const subDatas = subDados.datas.sort((a, b) => a - b);
                    const subDataAntiga = subDatas.length > 0 
                        ? subDatas[0].toLocaleDateString('pt-BR') 
                        : '-';
                    const subDataRecente = subDatas.length > 0 
                        ? subDatas[subDatas.length - 1].toLocaleDateString('pt-BR') 
                        : '-';
                    
                    const trSub = document.createElement('tr');
                    trSub.className = 'table-row transition-colors hover:bg-gray-50 border-l-4 border-gray-200';
                    trSub.innerHTML = `
                        <td class="px-4 py-3 pl-8">
                            <div class="flex items-center gap-2">
                                <span class="text-xs text-gray-400">└</span>
                                <span class="text-sm text-gray-700">${motivoData.motivo} - ${submotivo}</span>
                            </div>
                        </td>
                        <td class="px-4 py-3 text-center">
                            <span class="text-sm text-gray-700">${subDados.count}</span>
                        </td>
                        <td class="px-4 py-3 text-center">
                            <span class="text-xs text-gray-500">${subPercentual}%</span>
                        </td>
                        <td class="px-4 py-3 text-center">
                            ${subDados.foraPrazo > 0 
                                ? `<span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-50 text-red-600">${subDados.foraPrazo}</span>`
                                : `<span class="text-xs text-gray-300">-</span>`
                            }
                        </td>
                        <td class="px-4 py-3 text-center">
                            <span class="text-xs text-gray-500">${subDados.count - subDados.foraPrazo}</span>
                        </td>
                        <td class="px-4 py-3 text-center">
                            <span class="text-xs text-gray-500">${subDataAntiga}</span>
                        </td>
                        <td class="px-4 py-3 text-center">
                            <span class="text-xs text-gray-500">${subDataRecente}</span>
                        </td>
                        <td class="px-4 py-3">
                            <div class="flex items-center gap-2">
                                <div class="flex-1 bg-gray-100 rounded-full h-1.5 max-w-[100px]">
                                    <div class="${colorClass} h-1.5 rounded-full opacity-60" style="width: ${subPercentual}%"></div>
                                </div>
                            </div>
                        </td>
                    `;
                    ocorrenciaTbody.appendChild(trSub);
                });
            });
        });

        // Timeline chart
        const timelineCounts = {};
        rawData.forEach(d => {
            if (d.Inicio) {
                const parts = d.Inicio.split('/');
                if (parts.length === 3) {
                    const date = `${parts[2]}-${parts[1]}-${parts[0]}`;
                    timelineCounts[date] = (timelineCounts[date] || 0) + 1;
                }
            }
        });
        const sortedDates = Object.keys(timelineCounts).sort();
        
        new Chart(document.getElementById('chartTimeline'), {
            type: 'line',
            data: {
                labels: sortedDates.map(d => d.split('-').reverse().join('/')),
                datasets: [{
                    label: 'Solicitações',
                    data: sortedDates.map(d => timelineCounts[d]),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#10b981',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { color: '#f3f4f6' } },
                    x: { grid: { display: false } }
                }
            }
        });

        // Render table
        function renderTable(data) {
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';
            
            data.slice(0, 50).forEach(row => {
                const tr = document.createElement('tr');
                tr.className = 'table-row transition-colors';
                
                const statusClass = row.Status?.toUpperCase().includes('PENDENTE') 
                    ? 'bg-yellow-100 text-yellow-700' 
                    : 'bg-green-100 text-green-700';
                
                const prazoClass = row.TempoResolucao?.toUpperCase().includes('FORA DE')
                    ? 'bg-red-100 text-red-700'
                    : 'bg-gray-100 text-gray-700';
                
                tr.innerHTML = `
                    <td class="px-6 py-4 text-sm font-medium text-gray-900">${row.Matricula}</td>
                    <td class="px-6 py-4 text-sm text-gray-600">${row.Nome}</td>
                    <td class="px-6 py-4 text-sm text-gray-600">${row.Setor}</td>
                    <td class="px-6 py-4"><span class="px-2.5 py-1 rounded-full text-xs font-medium ${statusClass}">${row.Status}</span></td>
                    <td class="px-6 py-4 text-sm text-gray-600">${row.Ocorrencia}</td>
                    <td class="px-6 py-4"><span class="px-2.5 py-1 rounded-full text-xs font-medium ${prazoClass}">${row.TempoResolucao}</span></td>
                    <td class="px-6 py-4 text-sm text-gray-600">${row.Inicio}</td>
                `;
                tbody.appendChild(tr);
            });
            
            document.getElementById('rowCount').textContent = Math.min(data.length, 50);
            document.getElementById('totalCount').textContent = data.length;
        }

        renderTable(rawData);
    </script>

    <!-- Modal Responsáveis -->
    <div id="modalResponsaveis" class="fixed inset-0 bg-black/50 hidden z-50 flex items-center justify-center">
        <div class="bg-white rounded-2xl shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
            <div class="p-6 border-b border-gray-100 flex items-center justify-between">
                <h2 class="text-xl font-semibold text-gray-900">Gerenciar Responsáveis</h2>
                <button id="closeModalResponsaveis" class="text-gray-400 hover:text-gray-600 transition">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            <div class="p-6 border-b border-gray-100">
                <div class="flex items-center gap-4">
                    <div class="flex-1">
                        <label class="text-sm font-medium text-gray-700 mb-1.5 block">Setor</label>
                        <select id="filterSetorModal" class="w-full bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary/20">
                            <option value="">Todos os setores</option>
                        </select>
                    </div>
                </div>
            </div>
            <div class="overflow-auto max-h-[60vh]">
                <table id="tableOcorrencias" class="w-full">
                    <thead class="bg-gray-50 sticky top-0">
                        <tr>
                            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Ocorrência</th>
                            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Motivo</th>
                            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">SubMotivo</th>
                            <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Responsável</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                    </tbody>
                </table>
            </div>
            <div class="p-6 border-t border-gray-100 flex justify-end gap-3">
                <button id="btnSalvarResponsavel" class="bg-primary hover:bg-primaryHover text-white px-6 py-2.5 rounded-lg text-sm font-medium transition">
                    Salvar Responsáveis
                </button>
            </div>
        </div>
    </div>

    <script>
        const btnResponsaveis = document.getElementById('btnResponsaveis');
        const modalResponsaveis = document.getElementById('modalResponsaveis');
        const closeModal = document.getElementById('closeModalResponsaveis');
        const filterSetorModal = document.getElementById('filterSetorModal');
        const tableOcorrencias = document.getElementById('tableOcorrencias');
        const btnSalvarResponsavel = document.getElementById('btnSalvarResponsavel');

        btnResponsaveis.addEventListener('click', (e) => {
            e.preventDefault();
            modalResponsaveis.classList.remove('hidden');
            populateSetorFilter(filterSetorModal);
            renderOcorrenciasModal();
        });

        closeModal.addEventListener('click', () => {
            modalResponsaveis.classList.add('hidden');
        });

        modalResponsaveis.addEventListener('click', (e) => {
            if (e.target === modalResponsaveis) {
                modalResponsaveis.classList.add('hidden');
            }
        });

        filterSetorModal.addEventListener('change', () => {
            renderOcorrenciasModal();
        });

        function populateSetorFilter(selectElement) {
            selectElement.innerHTML = '<option value="">Todos os setores</option>';
            const sectors = [...new Set(rawData.map(d => d.Setor).filter(Boolean))].sort();
            sectors.forEach(sector => {
                const option = document.createElement('option');
                option.value = sector;
                option.textContent = sector;
                selectElement.appendChild(option);
            });
        }

        function renderOcorrenciasModal() {
            const setorSelecionado = filterSetorModal.value;
            const dadosFiltrados = setorSelecionado 
                ? rawData.filter(d => d.Setor === setorSelecionado)
                : rawData;

            const ocorrenciasAgrupadas = {};
            dadosFiltrados.forEach(d => {
                const key = `${d.Ocorrencia || 'N/A'}|${d.Motivo || 'N/A'}|${d.SubMotivo || 'N/A'}`;
                if (!ocorrenciasAgrupadas[key]) {
                    ocorrenciasAgrupadas[key] = { ocorrencia: d.Ocorrencia, motivo: d.Motivo, submotivo: d.SubMotivo, responsavel: d.Responsavel || '' };
                }
            });

            const tbody = tableOcorrencias.querySelector('tbody');
            tbody.innerHTML = '';

            Object.values(ocorrenciasAgrupadas).forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="px-4 py-3 text-sm text-gray-900">${item.ocorrencia || '-'}</td>
                    <td class="px-4 py-3 text-sm text-gray-900">${item.motivo || '-'}</td>
                    <td class="px-4 py-3 text-sm text-gray-900">${item.submotivo || '-'}</td>
                    <td class="px-4 py-3">
                        <input type="text" class="responsavel-campo w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" 
                               value="${item.responsavel}" placeholder="Nome do responsável">
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        btnSalvarResponsavel.addEventListener('click', () => {
            const rows = tableOcorrencias.querySelectorAll('tbody tr');
            rows.forEach((row, index) => {
                const responsavel = row.querySelector('.responsavel-campo').value;
                const setorSelecionado = filterSetorModal.value;
                const dadosFiltrados = setorSelecionado 
                    ? rawData.filter(d => d.Setor === setorSelecionado)
                    : rawData;

                const ocorrenciasUnicas = [...new Set(dadosFiltrados.map(d => `${d.Ocorrencia}|${d.Motivo}|${d.SubMotivo}`))];
                if (index < ocorrenciasUnicas.length) {
                    const [ocorrencia, motivo, submotivo] = ocorrenciasUnicas[index].split('|');
                    dadosFiltrados.forEach(d => {
                        if (d.Ocorrencia === ocorrencia && d.Motivo === motivo && d.SubMotivo === submotivo) {
                            d.Responsavel = responsavel;
                        }
                    });
                }
            });

            // Criar JSON com responsáveis
            const responsaveisData = {};
            rawData.forEach(d => {
                if (d.Responsavel) {
                    const key = `${d.Setor || 'N/A'}|${d.Ocorrencia || 'N/A'}|${d.Motivo || 'N/A'}|${d.SubMotivo || 'N/A'}`;
                    responsaveisData[key] = {
                        setor: d.Setor,
                        ocorrencia: d.Ocorrencia,
                        motivo: d.Motivo,
                        submotivo: d.SubMotivo,
                        responsavel: d.Responsavel
                    };
                }
            });

            // Baixar arquivo JSON
            const jsonStr = JSON.stringify(responsaveisData, null, 2);
            const blob = new Blob([jsonStr], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'responsaveis_' + new Date().toISOString().split('T')[0] + '.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            alert('Responsáveis salvos com sucesso! Arquivo JSON baixado.');
            modalResponsaveis.classList.add('hidden');
        });
    </script>
</body>
</html>
"""

        # Prepare data
        data_json = json.dumps(data, ensure_ascii=False)
        last_update_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Replace placeholders
        html_content = html_template.replace("REPLACE_DATA_HERE", data_json)
        html_content = html_content.replace("REPLACE_TIME_HERE", last_update_str)

        # Save file
        output_path = Path("dashboard.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Dashboard HTML gerado: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Erro ao gerar HTML simples: {e}")
        import traceback

        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    generate_dashboard()
