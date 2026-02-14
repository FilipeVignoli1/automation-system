import csv
import os
import sys
import glob
from pathlib import Path

# Adiciona diretório raiz ao path
project_root = str(Path(__file__).resolve().parent.parent)
sys.path.append(project_root)

import config.settings as settings

def fix_latest_csv():
    data_dir = Path(settings.DATA_DIR)
    csv_files = list(data_dir.glob("tabela_*_p2_t0.csv"))
    
    if not csv_files:
        print("Nenhum arquivo encontrado.")
        return

    latest_csv = max(csv_files, key=os.path.getmtime)
    print(f"Verificando arquivo: {latest_csv}")

    with open(latest_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        print("Arquivo vazio.")
        return

    # Separa linhas em "blob" (multiline/transposta) e "clean" (dados normais)
    blob_rows = []
    clean_rows = []
    
    for row in rows:
        # Heurística: célula com muitas quebras de linha identifica o blob
        if any(len(cell) > 20 and cell.count('\n') > 5 for cell in row):
            blob_rows.append(row)
        else:
            # Filtra linhas vazias
            if any(c.strip() for c in row):
                clean_rows.append(row)

    # Cenário 1: Encontramos linhas limpas (dados reais) E uma linha blob (cabeçalhos)
    if len(clean_rows) > 5 and blob_rows:
        print(f"Encontrados {len(clean_rows)} registros limpos e cabeçalhos no blob. Mesclando...")
        
        # Extrai cabeçalhos da primeira linha do blob
        # Assume que a primeira linha de cada célula do blob é o nome da coluna
        blob = blob_rows[0]
        headers = []
        for cell in blob:
            # Pega a primeira linha não vazia da célula como header
            lines = cell.strip().split('\n')
            if lines:
                headers.append(lines[0].strip())
            else:
                headers.append(f"Column_{len(headers)}")
        
        # Verifica se número de colunas bate
        if len(headers) == len(clean_rows[0]):
            print("Número de colunas compatível.")
        else:
            print(f"Aviso: Cabeçalhos ({len(headers)}) vs Dados ({len(clean_rows[0])}). Ajustando...")
            # Se sobrar header, corta. Se faltar, adiciona genérico.
            if len(headers) > len(clean_rows[0]):
                headers = headers[:len(clean_rows[0])]
            while len(headers) < len(clean_rows[0]):
                headers.append(f"Col_{len(headers)}")

        # Salva: Headers + Clean Rows
        with open(latest_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(clean_rows)
        
        print("Arquivo corrigido usando linhas limpas.")
        return

    # Cenário 2: Só tem o blob (fallback para lógica de transposição antiga)
    first_row = rows[0]
    has_multiline = any('\n' in cell for cell in first_row)
    
    if has_multiline:
        print("Apenas tabela vertical encontrada (sem linhas limpas). Tentando transpor (risco de perda de dados)...")
        
        # Divide células em colunas
        columns = []
        max_len = 0
        for cell in first_row:
            col_values = [v.strip() for v in cell.split('\n')]
            columns.append(col_values)
            max_len = max(max_len, len(col_values))
        
        print(f"Máximo de linhas detectado: {max_len}")
        
        # Transpõe
        fixed_rows = []
        for i in range(max_len):
            new_row = []
            for col in columns:
                val = col[i] if i < len(col) else ""
                new_row.append(val)
            fixed_rows.append(new_row)
        
        # Salva
        with open(latest_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerows(fixed_rows)
            
        print(f"Arquivo corrigido (transposição) com {len(fixed_rows)} linhas.")
    else:
        print(f"Arquivo parece normal ({len(rows)} linhas). Nenhuma ação tomada.")

if __name__ == "__main__":
    fix_latest_csv()
