import time
import subprocess
import sys
import argparse
from datetime import datetime

def run_automation():
    """Executa o script principal em modo headless e completo."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando extração automática...")
    
    # Comando: python main.py --headless --full --dashboard
    # Nota: main.py sem args já faz full+dash, mas vamos ser explícitos e adicionar headless
    cmd = [sys.executable, "main.py", "--headless", "--full", "--dashboard"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Sucesso! Dashboard atualizado.")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Erro na execução:")
            print(result.stderr)
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Falha ao executar subprocesso: {e}")

def main():
    parser = argparse.ArgumentParser(description="Executor Automático do Sirius Dashboard")
    parser.add_argument("--interval", type=int, default=15, help="Intervalo em minutos entre execuções (padrão: 15)")
    args = parser.parse_args()
    
    interval_seconds = args.interval * 60
    
    print("="*50)
    print(f" INICIANDO AUTOMAÇÃO SIRIUS")
    print(f" Intervalo: {args.interval} minutos")
    print(f" Modo: Headless (Sem janela)")
    print("="*50)
    print("Pressione Ctrl+C para parar.")
    print("")

    try:
        while True:
            run_automation()
            
            print(f"Aguardando {args.interval} minutos para a próxima execução...")
            time.sleep(interval_seconds)
            
    except KeyboardInterrupt:
        print("\nAutomação parada pelo usuário.")

if __name__ == "__main__":
    main()
