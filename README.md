# Sistema de Automação e Extração de Dados

Sistema para automatizar a extração de dados do portal Sirius usando Selenium.

## 📁 Estrutura

```
automation-system/
├── config/
│   ├── credentials.env.example  # Exemplo de configuração
│   └── settings.py              # Configurações do sistema
├── src/
│   ├── scraper.py               # Módulo principal de extração
│   ├── browser.py               # Gerenciamento do navegador
│   └── utils.py                 # Funções auxiliares
├── data/                        # Dados extraídos
├── logs/                        # Logs de execução
├── main.py                      # Script principal
└── requirements.txt
```

## 🚀 Instalação

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure suas credenciais:
```bash
cp config/credentials.env.example config/credentials.env
# Edite o arquivo config/credentials.env com suas credenciais
```

3. Baixe o ChromeDriver compatível com sua versão do Chrome:
- Acesse: https://chromedriver.chromium.org/downloads
- Ou use: `webdriver-manager` (já incluso nas dependências)

## 💻 Uso

### Extração básica:
```bash
python main.py
```

### Com opções:
```bash
# Modo headless (sem abrir navegador)
python main.py --headless

# Salvar em formato específico
python main.py --format csv
python main.py --format json
python main.py --format excel

# Extrair dados específicos
python main.py --module dashboard
```

## 📈 Dashboard

### Gerar dashboard completo (Extração + Visualização):
```bash
python main.py --painel --dashboard
```

### Apenas regenerar visualização (usando dados já extraídos):
```bash
python main.py --dashboard
```

## ⚙️ Configuração

Edite o arquivo `config/credentials.env`:

```env
SIRIUS_URL=https://sirius.assim.com.br/appdesktop/index.php
SIRIUS_USERNAME=vignoli
SIRIUS_PASSWORD=sua_senha_aqui
```

**IMPORTANTE:** Nunca commite o arquivo `credentials.env` com senhas reais!

## 📊 Saída de Dados

Os dados são salvos em:
- `data/extracted_YYYY-MM-DD_HH-MM-SS.json`
- `data/extracted_YYYY-MM-DD_HH-MM-SS.csv`
- `data/extracted_YYYY-MM-DD_HH-MM-SS.xlsx`

## 🔒 Segurança

- As credenciais são carregadas de variáveis de ambiente
- Logs não armazenam senhas
- Recomenda-se usar em ambiente seguro

## 🛠️ Tecnologias

- Python 3.8+
- Selenium WebDriver
- webdriver-manager
- pandas (para processamento de dados)
- python-dotenv (para variáveis de ambiente)
