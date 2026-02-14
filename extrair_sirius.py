#!/usr/bin/env python3
"""
Script de extração específica para Sirius
Fluxo: Login -> Workflow -> Painel -> Extração de dados
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.scraper import SiriusScraper
from src.utils import setup_logging, save_data

logger = setup_logging()


def extrair_dados_sirius():
    """Executa o fluxo completo de extração"""

    scraper = SiriusScraper(headless=False)

    try:
        # 1. Inicia navegador
        logger.info("=" * 60)
        logger.info("INICIANDO AUTOMAÇÃO SIRIUS")
        logger.info("=" * 60)
        scraper.start()

        # 2. Login
        logger.info("\n1. FAZENDO LOGIN...")
        if not scraper.login():
            logger.error("Falha no login!")
            return

        logger.info("✓ Login realizado com sucesso!")

        # Aguarda carregamento da página inicial
        time.sleep(3)

        # 3. Navegar para Workflow
        logger.info("\n2. NAVEGANDO PARA WORKFLOW...")
        if not scraper.navigate_to_workflow():
            logger.error("Não foi possível acessar o Workflow!")
            # Tenta salvar screenshot para debug
            scraper.driver.save_screenshot("workflow_erro.png")
            return

        logger.info("✓ Workflow acessado!")

        # 4. Extrair dados do Workflow
        logger.info("\n3. EXTRAINDO DADOS DO WORKFLOW...")
        workflow_data = scraper.extract_workflow_data()
        scraper.extracted_data.append({"page": "workflow", "data": workflow_data})
        logger.info("✓ Dados do Workflow extraídos!")

        # 5. Navegar para Painel
        logger.info("\n4. NAVEGANDO PARA PAINEL...")
        if not scraper.navigate_to_painel():
            logger.error("Não foi possível acessar o Painel!")
            scraper.driver.save_screenshot("painel_erro.png")
            return

        logger.info("✓ Painel acessado!")

        # 6. Extrair dados do Painel
        logger.info("\n5. EXTRAINDO DADOS DO PAINEL...")
        painel_data = scraper.extract_all_data()
        scraper.extracted_data.append({"page": "painel", "data": painel_data})
        logger.info("✓ Dados do Painel extraídos!")

        # 7. Salvar dados
        logger.info("\n6. SALVANDO DADOS...")

        # Salvar em JSON
        json_path = save_data(scraper.extracted_data, format="json")
        logger.info(f"✓ Dados salvos em JSON: {json_path}")

        # Salvar em CSV
        csv_path = save_data(scraper.extracted_data, format="csv")
        logger.info(f"✓ Dados salvos em CSV: {csv_path}")

        logger.info("\n" + "=" * 60)
        logger.info("EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
        logger.info("=" * 60)

        # Aguarda usuário ver os dados
        logger.info("\nPressione ENTER para fechar o navegador...")
        input()

    except Exception as e:
        logger.error(f"Erro durante execução: {e}")
        import traceback

        logger.error(traceback.format_exc())

        # Salva screenshot do erro
        try:
            scraper.driver.save_screenshot("erro_execucao.png")
            logger.info("Screenshot do erro salvo: erro_execucao.png")
        except:
            pass

    finally:
        scraper.quit()
        logger.info("Navegador fechado.")


if __name__ == "__main__":
    extrair_dados_sirius()
