#!/usr/bin/env python3
"""
Script de diagnóstico - Descobre elementos da página
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import time
from selenium.webdriver.common.by import By
from src.scraper import SiriusScraper
from src.utils import setup_logging

logger = setup_logging()


def discover_page_elements():
    """Descobre todos os elementos interativos da página"""

    scraper = SiriusScraper(headless=False)

    try:
        scraper.start()

        if scraper.login():
            logger.info("=" * 60)
            logger.info("MODO DE DIAGNÓSTICO")
            logger.info("=" * 60)
            logger.info("Analisando página após login...")

            # Aguarda página carregar completamente
            time.sleep(3)

            # Tira screenshot da página completa
            scraper.driver.save_screenshot("diagnostico_pagina.png")
            logger.info("Screenshot salvo: diagnostico_pagina.png")

            # Lista todos os links
            logger.info("\n" + "=" * 60)
            logger.info("LINKS ENCONTRADOS:")
            logger.info("=" * 60)
            links = scraper.driver.find_elements(By.TAG_NAME, "a")
            for i, link in enumerate(links[:20], 1):  # Primeiros 20 links
                try:
                    texto = link.text.strip()
                    href = link.get_attribute("href")
                    if texto:
                        logger.info(f"{i}. Texto: '{texto}' | href: {href}")
                except:
                    pass

            # Lista todos os botões
            logger.info("\n" + "=" * 60)
            logger.info("BOTÕES ENCONTRADOS:")
            logger.info("=" * 60)
            botoes = scraper.driver.find_elements(By.TAG_NAME, "button")
            for i, botao in enumerate(botoes[:15], 1):
                try:
                    texto = botao.text.strip()
                    if texto:
                        logger.info(f"{i}. Texto: '{texto}'")
                except:
                    pass

            # Lista elementos com classe 'menu'
            logger.info("\n" + "=" * 60)
            logger.info("ELEMENTOS DE MENU:")
            logger.info("=" * 60)
            menus = scraper.driver.find_elements(
                By.CSS_SELECTOR, "[class*='menu'], [id*='menu']"
            )
            for i, menu in enumerate(menus[:15], 1):
                try:
                    texto = menu.text.strip()[:50]  # Limita texto
                    classes = menu.get_attribute("class")
                    id_attr = menu.get_attribute("id")
                    if texto:
                        logger.info(f"{i}. Texto: '{texto}'")
                        if classes:
                            logger.info(f"   Classe: {classes}")
                        if id_attr:
                            logger.info(f"   ID: {id_attr}")
                except:
                    pass

            # Procura especificamente por Workflow e Painel
            logger.info("\n" + "=" * 60)
            logger.info("BUSCANDO 'WORKFLOW' E 'PAINEL':")
            logger.info("=" * 60)

            # Busca por texto
            todos_elementos = scraper.driver.find_elements(
                By.XPATH,
                "//*[contains(text(), 'Workflow') or contains(text(), 'workflow') or contains(text(), 'PAINEL') or contains(text(), 'Painel') or contains(text(), 'painel')]",
            )
            for i, elem in enumerate(todos_elementos[:10], 1):
                try:
                    texto = elem.text.strip()
                    tag = elem.tag_name
                    logger.info(f"{i}. [{tag}] '{texto}'")
                except:
                    pass

            logger.info("\n" + "=" * 60)
            logger.info("DIAGNÓSTICO COMPLETO!")
            logger.info("=" * 60)
            logger.info("Verifique o arquivo 'diagnostico_pagina.png'")
            logger.info("e os logs acima para identificar os elementos.")
            logger.info("\nPressione ENTER para fechar o navegador...")
            input()

        else:
            logger.error("Falha no login")

    except Exception as e:
        logger.error(f"Erro: {e}")
    finally:
        scraper.quit()


if __name__ == "__main__":
    discover_page_elements()
