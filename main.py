#!/usr/bin/env python3
"""
Sistema de Automação e Extração de Dados - Sirius
Script principal
"""

import argparse
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.scraper import SiriusScraper
from src.utils import setup_logging
from src.dashboard_gen import generate_dashboard
from config import settings

logger = setup_logging()


def main():
    parser = argparse.ArgumentParser(
        description="Sistema de extração de dados do Sirius",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py                          # Execução padrão (página inicial)
  python main.py --headless               # Modo headless (sem interface)
  python main.py --format csv             # Salvar como CSV
  python main.py --format all             # Salvar em todos os formatos
  python main.py --debug                  # Modo debug (mais logs)
  python main.py --workflow               # Navegar para Workflow
  python main.py --painel                 # Navegar para Painel
  python main.py --full                   # Workflow + Painel completo
  python main.py --dashboard              # Gerar dashboard a partir dos dados (pode combinar)
        """,
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Executar em modo headless (sem abrir navegador)",
    )

    parser.add_argument(
        "--format",
        choices=["json", "csv", "all"],
        default="json",
        help="Formato de saída dos dados (padrão: json)",
    )

    parser.add_argument(
        "--debug", action="store_true", help="Ativar modo debug com mais logs"
    )

    parser.add_argument(
        "--module", type=str, help="Módulo específico para extrair dados"
    )

    parser.add_argument(
        "--workflow",
        action="store_true",
        help="Navegar para Workflow após login",
    )

    parser.add_argument(
        "--painel",
        action="store_true",
        help="Navegar para Painel após Workflow",
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="Executar navegação completa (Workflow + Painel)",
    )
    
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Gerar dashboard HTML após extração (ou sozinho se nenhuma extração for feita)",
    )

    args = parser.parse_args()

    # Configura nível de log
    if args.debug:
        import logging

        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("=" * 50)
    logger.info("Iniciando Sistema de Automação Sirius")
    logger.info("=" * 50)

    # Valida credenciais
    if not settings.SIRIUS_USERNAME or not settings.SIRIUS_PASSWORD:
        logger.error("Credenciais não configuradas!")
        logger.error("Edite o arquivo config/credentials.env")
        sys.exit(1)
        
    # Verifica se deve executar extração
    # Se nenhum argumento de ação for passado, assume execução completa (full + dashboard)
    no_action_args = not (args.workflow or args.painel or args.module or args.full or args.dashboard)
    
    if no_action_args:
        logger.info("Nenhum argumento específico fornecido. Executando modo COMPLETO (Extração + Dashboard).")
        args.full = True
        args.dashboard = True
    
    should_extract = args.workflow or args.painel or args.module or args.full or (not args.dashboard)
    
    if should_extract:
        # Executa extração
        try:
            # Se --full for usado, ativa workflow e painel
            if args.full:
                args.workflow = True
                args.painel = True

            # Se nenhuma opção de navegação for especificada, extrai só a página inicial
            if not args.workflow and not args.painel and not args.module:
                # Mas só se não for apenas dashboard
                if not args.dashboard:
                    with SiriusScraper(headless=args.headless) as scraper:
                        if scraper.login():
                            logger.info("Login realizado com sucesso!")
                            scraper.extract_all_data()

                            if args.format == "all":
                                scraper.save("json")
                                scraper.save("csv")
                            else:
                                scraper.save(args.format)
                            
                            scraper.save_tables()
                            logger.info("Processo concluído com sucesso!")
                        else:
                            logger.error("Falha no login. Verifique suas credenciais.")
                            sys.exit(1)
            else:
                # Executa navegação completa com workflow e/ou painel
                scraper = SiriusScraper(headless=args.headless)
                scraper.run_full_extraction(
                    headless=args.headless, workflow=args.workflow, painel=args.painel
                )

        except KeyboardInterrupt:
            logger.info("\nOperação cancelada pelo usuário")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Erro fatal: {e}")
            sys.exit(1)
            
    # Gera dashboard se solicitado
    if args.dashboard:
        logger.info("=" * 50)
        logger.info("GERANDO DASHBOARD")
        logger.info("=" * 50)
        if generate_dashboard():
            logger.info("Dashboard gerado com sucesso!")
        else:
            logger.error("Falha ao gerar dashboard.")


if __name__ == "__main__":
    main()
