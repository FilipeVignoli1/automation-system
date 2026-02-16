# Sirius Dashboard - React + TypeScript

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
