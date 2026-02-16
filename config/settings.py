import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
env_path = os.path.join(os.path.dirname(__file__), "credentials.env")
load_dotenv(env_path)

# Credenciais
SIRIUS_URL = os.getenv("SIRIUS_URL", "https://sirius.assim.com.br/appdesktop/index.php")
SIRIUS_USERNAME = os.getenv("SIRIUS_USERNAME", "")
SIRIUS_PASSWORD = os.getenv("SIRIUS_PASSWORD", "")
SIRIUS_2FA_CODE = os.getenv("SIRIUS_2FA_CODE", "")

# Configurações do navegador
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30"))
IMPLICIT_WAIT = int(os.getenv("IMPLICIT_WAIT", "10"))

# Configurações de exportação
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

# Garante que os diretórios existam
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
