// components/DataTable.tsx
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
