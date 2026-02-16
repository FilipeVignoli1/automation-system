// types/index.ts
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
