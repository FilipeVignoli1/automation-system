import csv
import json
import glob
import os
from pathlib import Path
from src.utils import setup_logging
import config.settings as settings

logger = setup_logging()

def generate_dashboard():
    """Gera um dashboard HTML a partir do arquivo CSV mais recente."""
    try:
        logger.info("Iniciando geração do dashboard...")
        
        # 1. Encontrar o arquivo CSV mais recente e relevante
        # Prioriza arquivos que contenham "_p2_" (painel geralmente) e sejam maiores
        
        data_dir = Path(settings.DATA_DIR)
        csv_files = list(data_dir.glob("tabela_*_p*_t*.csv"))
        
        if not csv_files:
            logger.error("Nenhum arquivo CSV de tabela encontrado em 'data/'.")
            return False
            
        # Filtra arquivos muito pequenos (menos de 100 bytes)
        csv_files = [f for f in csv_files if f.stat().st_size > 100]
        
        if not csv_files:
             logger.error("Nenhum arquivo CSV com dados encontrado.")
             return False

        # Tenta encontrar tabelas do painel (p2)
        painel_files = [f for f in csv_files if "_p2_" in f.name]
        
        if painel_files:
             # Se houver tabelas de painel, pega a mais recente entre elas
             latest_csv = max(painel_files, key=os.path.getmtime)
        else:
             # Se não, pega o maior arquivo recente (assumindo que seja a tabela de dados)
             latest_csv = max(csv_files, key=lambda f: f.stat().st_size)
             
        logger.info(f"Usando arquivo CSV: {latest_csv.name}")
        
        # 2. Ler e limpar dados
        data_rows = []
        headers = [
            'Matricula', 'Nome', 'Ficha', 'Prioridade', 'FollowUp', 'Setor', 
            'Status', 'Usuario', 'Macro', 'Ocorrencia', 'Motivo', 'SubMotivo', 
            'Inicio', 'TempoResolucao', 'PrazoSetor', 'Conclusao'
        ]
        
        with open(latest_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                # Filtra linhas de "lixo" (filtros do sistema)
                # Dados reais têm ~16 colunas preenchidas ou vazias, mas a estrutura é consistente.
                # Linhas de filtro geralmente têm 1 coluna ou formato diferente.
                if len(row) >= 10:
                    # Cria dicionário
                    # Garante que row tenha tamanho suficiente (preenche com vazio se necessario)
                    while len(row) < len(headers):
                        row.append("")
                        
                    row_dict = {headers[i]: row[i].strip() for i in range(len(headers))}
                    
                    # Filtra linha de filtro "TODOS" e cabeçalho repetido "Matricula"
                    # Verifica se o valor da coluna 'Matricula' é um dos valores a ignorar
                    val_matricula = row_dict['Matricula'].upper()
                    if val_matricula in ['TODOS', 'MATRICULA']:
                        continue
                        
                    data_rows.append(row_dict)
                    
        logger.info(f"Processadas {len(data_rows)} linhas de dados.")
        
        if not data_rows:
            logger.warning("Nenhum dado válido encontrado no CSV.")
            return False

        # 3. Gerar HTML
        html_content = create_html_template(data_rows)
        
        # 4. Salvar arquivo
        output_file = Path("dashboard.html")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        logger.info(f"Dashboard gerado com sucesso: {output_file.absolute()}")
        return True

    except Exception as e:
        logger.error(f"Erro ao gerar dashboard: {e}")
        return False

def create_html_template(data):
    """Cria o conteúdo HTML do dashboard com os dados injetados."""
    
    json_data = json.dumps(data)
    
    return f"""
<!DOCTYPE html>
<html lang="pt-br" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="60"> <!-- Auto-refresh a cada 60s -->
    <title>Sirius Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    colors: {{
                        primary: '#0ea5e9',
                        secondary: '#6366f1',
                        dark: '#0f172a',
                        darker: '#020617',
                        card: '#1e293b'
                    }}
                }}
            }}
        }}
    </script>
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        :root {{ color-scheme: dark; }}
    </style>
</head>
<body class="bg-darker text-gray-100 min-h-screen">

    <!-- Navbar -->
    <nav class="bg-card border-b border-gray-800 px-6 py-4 flex justify-between items-center">
        <div class="flex items-center gap-3">
            <div class="bg-primary/20 p-2 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 002 2h2a2 2 0 002-2z" />
                </svg>
            </div>
            <h1 class="text-xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">Sirius Dashboard</h1>
        </div>
        <div class="text-sm text-gray-400">
            Atualizado: <span id="last-updated">Hoje</span>
        </div>
    </nav>

    <main class="p-6 max-w-[1600px] mx-auto space-y-6">
        
        <!-- KPI Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <!-- Total -->
            <div class="bg-card p-4 rounded-xl border border-gray-800 hover:border-primary/50 transition duration-300">
                <h3 class="text-gray-400 text-sm font-medium">Total de Solicitações</h3>
                <p class="text-3xl font-bold mt-2 text-white" id="kpi-total">0</p>
            </div>
            
            <!-- Pendentes -->
            <div class="bg-card p-4 rounded-xl border border-gray-800 hover:border-yellow-500/50 transition duration-300">
                <h3 class="text-gray-400 text-sm font-medium">Pendentes</h3>
                <div class="flex items-end gap-2">
                    <p class="text-3xl font-bold mt-2 text-yellow-400" id="kpi-pending">0</p>
                    <span class="text-sm text-yellow-400/60 mb-1" id="kpi-pending-pct">(0%)</span>
                </div>
            </div>

            <!-- Fora do Prazo -->
            <div class="bg-card p-4 rounded-xl border border-gray-800 hover:border-red-500/50 transition duration-300">
                <h3 class="text-gray-400 text-sm font-medium">Fora do Prazo</h3>
                <div class="flex items-end gap-2">
                    <p class="text-3xl font-bold mt-2 text-red-400" id="kpi-late">0</p>
                    <span class="text-sm text-red-400/60 mb-1" id="kpi-late-pct">(0%)</span>
                </div>
            </div>

             <!-- Setores -->
            <div class="bg-card p-4 rounded-xl border border-gray-800 hover:border-green-500/50 transition duration-300">
                <h3 class="text-gray-400 text-sm font-medium">Setores Ativos</h3>
                <p class="text-3xl font-bold mt-2 text-green-400" id="kpi-sectors">0</p>
            </div>
        </div>

        <!-- Charts Row 1 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="bg-card p-6 rounded-xl border border-gray-800">
                <h3 class="text-lg font-semibold mb-4 text-gray-200">Volume por Setor</h3>
                <div class="h-64">
                    <canvas id="chart-sector"></canvas>
                </div>
            </div>
            <div class="bg-card p-6 rounded-xl border border-gray-800">
                <h3 class="text-lg font-semibold mb-4 text-gray-200">Top 5 Motivos</h3>
                <div class="h-64">
                    <canvas id="chart-motivo"></canvas>
                </div>
            </div>
        </div>

        <!-- Charts Row 2 -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div class="bg-card p-6 rounded-xl border border-gray-800 lg:col-span-1">
                <h3 class="text-lg font-semibold mb-4 text-gray-200">Status dos Pedidos</h3>
                <div class="h-64 flex justify-center">
                    <canvas id="chart-status"></canvas>
                </div>
            </div>
            <div class="bg-card p-6 rounded-xl border border-gray-800 lg:col-span-2">
                 <h3 class="text-lg font-semibold mb-4 text-gray-200">Solicitações por Dia (Início)</h3>
                <div class="h-64">
                    <canvas id="chart-timeline"></canvas>
                </div>
            </div>
        </div>

        <!-- Data Table -->
        <div class="bg-card rounded-xl border border-gray-800 overflow-hidden">
            <div class="p-6 border-b border-gray-800 flex justify-between items-center">
                <h3 class="text-lg font-semibold text-gray-200">Detalhamento</h3>
                <input type="text" id="search-input" placeholder="Buscar..." class="bg-dark border border-gray-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-primary text-gray-300">
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm text-gray-400">
                    <thead class="bg-gray-800/50 text-gray-200 uppercase font-medium text-xs">
                        <tr>
                            <th class="px-6 py-3">Matrícula</th>
                            <th class="px-6 py-3">Nome</th>
                            <th class="px-6 py-3">Setor</th>
                            <th class="px-6 py-3">Status</th>
                            <th class="px-6 py-3">Ocorrência</th>
                            <th class="px-6 py-3">Prazo</th>
                            <th class="px-6 py-3">Início</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-800" id="table-body">
                        <!-- Rows injected by JS -->
                    </tbody>
                </table>
            </div>
            <div class="p-4 border-t border-gray-800 text-center text-xs text-gray-500">
                Mostrando <span id="row-count">0</span> registros
            </div>
        </div>

    </main>

    <script>
        // Inject Data from Python
        const rawData = {json_data}; 

        // --- Processing Data ---
        const total = rawData.length;
        const pending = rawData.filter(d => d.Status && d.Status.toUpperCase().includes('PENDENTE')).length;
        const late = rawData.filter(d => (d.TempoResolucao && d.TempoResolucao.toUpperCase().includes('FORA DE')) || (d.PrazoSetor && d.PrazoSetor.toUpperCase().includes('FORA DE'))).length;
        const sectors = [...new Set(rawData.map(d => d.Setor))].length;

        // UI Updates - KPIs
        document.getElementById('kpi-total').innerText = total;
        document.getElementById('kpi-pending').innerText = pending;
        document.getElementById('kpi-pending-pct').innerText = '(' + ((pending/total)*100).toFixed(1) + '%)';
        document.getElementById('kpi-late').innerText = late;
        document.getElementById('kpi-late-pct').innerText = '(' + ((late/total)*100).toFixed(1) + '%)';
        document.getElementById('kpi-sectors').innerText = sectors;
        
        // --- Charts Helper ---
        function getCounts(field) {{
            const counts = {{}};
            rawData.forEach(d => {{
                const val = d[field] || 'N/A';
                counts[val] = (counts[val] || 0) + 1;
            }});
            return Object.entries(counts).sort((a,b) => b[1] - a[1]);
        }}

        // Sector Chart
        const sectorData = getCounts('Setor').slice(0, 10);
        new Chart(document.getElementById('chart-sector'), {{
            type: 'bar',
            data: {{
                labels: sectorData.map(d => d[0]),
                datasets: [{{
                    label: 'Solicitações',
                    data: sectorData.map(d => d[1]),
                    backgroundColor: '#0ea5e9',
                    borderRadius: 4
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ grid: {{ color: '#334155' }} }}, x: {{ grid: {{ display: false }} }} }} }}
        }});

        // Top Motivos
        const motivoData = getCounts('Motivo').slice(0, 5);
        new Chart(document.getElementById('chart-motivo'), {{
            type: 'bar',
            data: {{
                labels: motivoData.map(d => d[0]),
                datasets: [{{
                    label: 'Ocorrências',
                    data: motivoData.map(d => d[1]),
                    backgroundColor: '#6366f1',
                    borderRadius: 4,
                    indexAxis: 'y'
                }}]
            }},
            options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ grid: {{ color: '#334155' }} }}, y: {{ grid: {{ display: false }} }} }} }}
        }});
        
        // Status Chart
        const statusData = getCounts('Status');
        new Chart(document.getElementById('chart-status'), {{
            type: 'doughnut',
            data: {{
                labels: statusData.map(d => d[0]),
                datasets: [{{
                    data: statusData.map(d => d[1]),
                    backgroundColor: ['#eab308', '#22c55e', '#ef4444', '#3b82f6', '#a855f7'],
                    borderWidth: 0
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'bottom', labels: {{ color: '#94a3b8' }} }} }} }}
        }});

        // Timeline
        const timelineCounts = {{}};
        rawData.forEach(d => {{
            if(d.Inicio) {{
                // Parse date assuming DD/MM/YYYY
                const parts = d.Inicio.split('/');
                if(parts.length === 3) {{
                    const date = parts[2] + '-' + parts[1] + '-' + parts[0]; // YYYY-MM-DD for sorting
                    timelineCounts[date] = (timelineCounts[date] || 0) + 1;
                }}
            }}
        }});
        const sortedDates = Object.keys(timelineCounts).sort();
        
        new Chart(document.getElementById('chart-timeline'), {{
            type: 'line',
            data: {{
                labels: sortedDates.map(d => d.split('-').reverse().join('/')),
                datasets: [{{
                    label: 'Solicitações',
                    data: sortedDates.map(d => timelineCounts[d]),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ y: {{ grid: {{ color: '#334155' }} }}, x: {{ grid: {{ display: false }} }} }} }}
        }});

        // --- Table Rendering ---
        const tbody = document.getElementById('table-body');
        const searchInput = document.getElementById('search-input');
        
        function renderTable(data) {{
            tbody.innerHTML = '';
            // Limit to 100 rows for performance in this simple view
            data.slice(0, 100).forEach(row => {{
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-gray-800/50 transition duration-150';
                
                // Helper for status color
                let statusColor = 'text-gray-400';
                if(row.Status === 'PENDENTE') statusColor = 'text-yellow-400';
                
                // Helper for deadline color
                let prazoClass = 'bg-gray-800 text-gray-400';
                if(row.TempoResolucao === 'FORA DE PRAZO') prazoClass = 'bg-red-500/10 text-red-500 border border-red-500/20';
                
                tr.innerHTML = `
                    <td class="px-6 py-4 font-medium text-gray-200">${{row.Matricula}}</td>
                    <td class="px-6 py-4">${{row.Nome}}</td>
                    <td class="px-6 py-4">${{row.Setor}}</td>
                    <td class="px-6 py-4 ${{statusColor}}">${{row.Status}}</td>
                    <td class="px-6 py-4">${{row.Ocorrencia}}</td>
                    <td class="px-6 py-4">
                        <span class="px-2 py-1 rounded text-xs ${{prazoClass}}">
                            ${{row.TempoResolucao}}
                        </span>
                    </td>
                    <td class="px-6 py-4">${{row.Inicio}}</td>
                `;
                tbody.appendChild(tr);
            }});
            document.getElementById('row-count').innerText = data.length;
        }}
        
        renderTable(rawData);

        // Search functionality
        searchInput.addEventListener('input', (e) => {{
            const term = e.target.value.toLowerCase();
            const filtered = rawData.filter(row => 
                Object.values(row).some(val => String(val).toLowerCase().includes(term))
            );
            renderTable(filtered);
        }});

    </script>
</body>
</html>
    """

if __name__ == "__main__":
    generate_dashboard()
