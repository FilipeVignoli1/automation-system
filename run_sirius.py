#!/usr/bin/env python3
"""
Script simples para extração completa do Sirius
Comando: python run_sirius.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.scraper import SiriusScraper
from src.utils import setup_logging

logger = setup_logging()

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("EXTRAÇÃO SIRIUS - WORKFLOW + FINANCEIRO")
    logger.info("=" * 60)

    # Executa extração completa
    scraper = SiriusScraper(headless=False)
    scraper.run_full_extraction(headless=False, workflow=True, painel=True)

    logger.info("\nProcesso finalizado!")
    logger.info("Verifique a pasta 'data/' para os arquivos extraídos.")
