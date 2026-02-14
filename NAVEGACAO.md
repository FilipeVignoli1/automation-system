# Navegação Workflow e Painel

O sistema agora suporta navegação automática para as seções **Workflow** e **Painel** do Sirius.

## 🚀 Como usar

### 1. Extrair só a página inicial (padrão):
```bash
python main.py
```

### 2. Navegar para Workflow:
```bash
python main.py --workflow
```

Fluxo:
- Login → Workflow (extrai dados)

### 3. Navegar para Painel:
```bash
python main.py --painel
```

Fluxo:
- Login → Painel (extrai dados)

### 4. Workflow completo (Workflow + Painel):
```bash
python main.py --full
```

Fluxo:
- Login → Workflow (extrai dados) → Painel (extrai dados)

### 5. Combinar opções:
```bash
# Workflow + Painel em CSV
python main.py --full --format csv

# Só Workflow em modo headless
python main.py --workflow --headless

# Painel com debug
python main.py --painel --debug
```

## 📊 Saída de Dados

Os dados são salvos separadamente para cada página:
- `data/extracted_..._inicial.json` - Página inicial
- `data/extracted_..._workflow.json` - Página Workflow
- `data/extracted_..._painel.json` - Página Painel

## ⚠️ Ajustes necessários

Se os seletores não funcionarem, o sistema salvará screenshots de debug:
- `workflow_not_found.png`
- `painel_not_found.png`

Você pode inspecionar essas imagens e ajustar os seletores em `src/scraper.py` nos métodos:
- `navigate_to_workflow()`
- `navigate_to_painel()`

## 🔧 Ajustando seletores

Se os menus tiverem nomes diferentes, edite o arquivo `src/scraper.py` e altere as listas:

```python
# Para Workflow
workflow_selectors = [
    "a[href*='workflow']",
    "a:contains('Workflow')",
    # Adicione seus seletores aqui
]

# Para Painel
painel_selectors = [
    "a[href*='painel']",
    "a:contains('Painel')",
    # Adicione seus seletores aqui
]
```
