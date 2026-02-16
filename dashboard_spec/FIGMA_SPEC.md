# Especificação Figma - Sirius Dashboard

## 📐 Layout System

### Grid
- **Container máximo**: 1600px
- **Padding**: 24px (p-6)
- **Gap entre cards**: 16px (gap-4)
- **Grid responsivo**: 
  - Mobile: 1 coluna
  - Tablet: 2 colunas
  - Desktop: 4 colunas (KPIs), 2 colunas (charts)

### Cores (Dark Mode)

#### Backgrounds
- **Primary BG**: `#0f172a` (slate-900)
- **Card BG**: `#1e293b` (slate-800)
- **Darker BG**: `#020617` (slate-950)
- **Input BG**: `#0f172a` (slate-900)

#### Textos
- **Heading**: `#f8fafc` (white)
- **Body**: `#94a3b8` (gray-400)
- **Muted**: `#64748b` (gray-500)

#### Cores de Status
- **Primary**: `#0ea5e9` (sky-500)
- **Success**: `#22c55e` (green-500)
- **Warning**: `#eab308` (yellow-500)
- **Danger**: `#ef4444` (red-500)
- **Secondary**: `#6366f1` (indigo-500)

#### Bordas
- **Default**: `#1e293b` (gray-800)
- **Hover**: Com 50% de opacidade da cor primária

## 🧩 Componentes

### 1. Navbar
- **Altura**: 64px
- **Background**: `#1e293b`
- **Border-bottom**: 1px solid `#1e293b`
- **Padding**: 24px horizontal, 16px vertical
- **Shadow**: subtle

### 2. KPI Card
- **Background**: `#1e293b`
- **Border**: 1px solid `#1e293b`
- **Border-radius**: 12px
- **Padding**: 16px
- **Hover**: Border color muda para cor do status
- **Título**: 14px, medium, gray-400
- **Valor**: 30px, bold, cor do status

**Estados:**
- Primary: border sky-500/50, text white
- Warning: border yellow-500/50, text yellow-400
- Danger: border red-500/50, text red-400
- Success: border green-500/50, text green-400

### 3. Chart Card
- **Background**: `#1e293b`
- **Border**: 1px solid `#1e293b`
- **Border-radius**: 12px
- **Padding**: 24px
- **Título**: 18px, semibold, gray-200
- **Chart height**: 256px

### 4. Data Table
- **Background**: `#1e293b`
- **Border**: 1px solid `#1e293b`
- **Border-radius**: 12px
- **Header**: 
  - Background: `#334155` (slate-700/50)
  - Text: 12px, uppercase, gray-200
  - Padding: 12px 24px
- **Row**:
  - Border-bottom: 1px solid `#1e293b`
  - Hover: bg slate-700/50
  - Padding: 16px 24px
  - Text: 14px, gray-400

### 5. Search Input
- **Background**: `#0f172a`
- **Border**: 1px solid `#374151`
- **Border-radius**: 8px
- **Padding**: 8px 16px 8px 40px (com ícone)
- **Width**: 256px
- **Placeholder**: gray-500
- **Focus**: border sky-500

### 6. Status Badge
- **Prazo OK**: bg slate-700, text gray-400
- **Fora do Prazo**: bg red-500/10, text red-500, border red-500/20
- **Border-radius**: 4px
- **Padding**: 4px 8px
- **Font**: 12px

## 📊 Dados para Prototipagem

**Total de Solicitações**: 82
**Pendentes**: 82 (100.0%)
**Fora do Prazo**: 30 (36.6%)
**Setores Ativos**: 1

### Gráficos

**Volume por Setor (Top 10):**
- GEREL / BACKOFFICE ADM: 82

**Top 5 Motivos:**
- RECLAME AQUI: 16
- REEMBOLSO: 15
- ANÁLISE DE COBERTURA: 7
- PLANO MÉDICO: 7
- SUGESTÕES: 6

**Status:**
- PENDENTE: 82

## 📝 Anotações de Design

### Tipografia
- **Fonte**: Inter, sans-serif
- **Headings**: Font-bold
- **Body**: Font-normal

### Espaçamento
- **xs**: 4px
- **sm**: 8px
- **md**: 16px
- **lg**: 24px
- **xl**: 32px

### Border Radius
- **sm**: 4px (badges)
- **md**: 8px (inputs)
- **lg**: 12px (cards)

### Sombras
- **Cards**: Subtle shadow on hover
- **Navbar**: shadow-sm

## 🎨 Protótipo Visual

### Estrutura da Página
```
┌─────────────────────────────────────────────────────────────┐
│  [Logo] Sirius Dashboard                    Atualizado: Hoje│
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Total    │ │Pendentes │ │Fora Prazo│ │ Setores  │       │
│  │   82     │ │  82      │ │   30      │ │   1       │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                                                             │
│  ┌──────────────────────────┐ ┌──────────────────────────┐  │
│  │ Volume por Setor         │ │ Top 5 Motivos            │  │
│  │ [Bar Chart]              │ │ [Horizontal Bar]         │  │
│  └──────────────────────────┘ └──────────────────────────┘  │
│                                                             │
│  ┌──────────────────┐ ┌───────────────────────────────────┐ │
│  │ Status           │ │ Timeline                          │ │
│  │ [Doughnut]       │ │ [Line Chart]                      │ │
│  └──────────────────┘ └───────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Detalhamento                              [Buscar...]   ││
│  │ ┌─────────────────────────────────────────────────────┐ ││
│  │ │ Matrícula │ Nome │ Setor │ Status │ ...            │ ││
│  │ └─────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---
**Gerado em**: 2026-02-16 13:29:36
