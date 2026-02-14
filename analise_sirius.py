#!/usr/bin/env python3
"""
Script de diagnóstico - Analisa a estrutura da página Sirius
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import time
import json
from selenium.webdriver.common.by import By
from src.scraper import SiriusScraper
from src.utils import setup_logging

logger = setup_logging()


def analisar_pagina():
    """Analisa a estrutura da página após login"""

    scraper = SiriusScraper(headless=False)

    try:
        scraper.start()

        if scraper.login():
            logger.info("=" * 70)
            logger.info("MODO DE ANÁLISE - AGUARDANDO CARREGAMENTO COMPLETO")
            logger.info("=" * 70)

            # Aguarda carregamento
            time.sleep(5)

            # Salva screenshot
            scraper.driver.save_screenshot("analise_pagina.png")
            logger.info("✓ Screenshot salvo: analise_pagina.png")

            # Extrai HTML completo
            html = scraper.driver.page_source
            with open("pagina_html.html", "w", encoding="utf-8") as f:
                f.write(html)
            logger.info("✓ HTML salvo: pagina_html.html")

            # Análise de links
            logger.info("\n" + "=" * 70)
            logger.info("LINKS ENCONTRADOS:")
            logger.info("=" * 70)
            links = scraper.driver.find_elements(By.TAG_NAME, "a")
            links_data = []
            for i, link in enumerate(links, 1):
                try:
                    texto = link.text.strip()
                    href = link.get_attribute("href")
                    if texto:
                        logger.info(f"{i}. '{texto}' -> {href}")
                        links_data.append({"texto": texto, "href": href})
                except:
                    pass

            # Salva links em JSON
            with open("links_encontrados.json", "w", encoding="utf-8") as f:
                json.dump(links_data, f, indent=2, ensure_ascii=False)
            logger.info("\n✓ Links salvos: links_encontrados.json")

            # Análise de botões
            logger.info("\n" + "=" * 70)
            logger.info("BOTÕES ENCONTRADOS:")
            logger.info("=" * 70)
            botoes = scraper.driver.find_elements(By.TAG_NAME, "button")
            for i, botao in enumerate(botoes[:20], 1):
                try:
                    texto = botao.text.strip()
                    if texto:
                        logger.info(f"{i}. '{texto}'")
                except:
                    pass

            # Busca específica por Workflow e Painel
            logger.info("\n" + "=" * 70)
            logger.info("BUSCANDO WORKFLOW E PAINEL:")
            logger.info("=" * 70)

            # Busca por texto em qualquer elemento
            elementos = scraper.driver.find_elements(
                By.XPATH,
                "//*[contains(translate(text(), 'WORKFLOWPAINEL', 'workflowpainel'), 'workflow') or contains(translate(text(), 'WORKFLOWPAINEL', 'workflowpainel'), 'painel')]",
            )

            for elem in elementos[:15]:
                try:
                    texto = elem.text.strip()
                    tag = elem.tag_name
                    xpath = scraper.driver.execute_script(
                        """
                        function getXPath(element) {
                            if (element.id !== '') return 'id(\"' + element.id + '\")';
                            if (element === document.body) return element.tagName;
                            var ix = 0;
                            var siblings = element.parentNode.childNodes;
                            for (var i = 0; i < siblings.length; i++) {
                                var sibling = siblings[i];
                                if (sibling === element) return getXPath(element.parentNode) + '/' + element.tagName + '[' + (ix + 1) + ']';
                                if (sibling.nodeType === 1 && sibling.tagName === element.tagName) ix++;
                            }
                        }
                        return getXPath(arguments[0]);
                    """,
                        elem,
                    )
                    logger.info(f"[{tag}] '{texto[:50]}'")
                    logger.info(f"   XPath: {xpath}")
                except:
                    pass

            # Extrai texto da página
            logger.info("\n" + "=" * 70)
            logger.info("TEXTO DA PÁGINA:")
            logger.info("=" * 70)
            try:
                body_text = scraper.driver.find_element(By.TAG_NAME, "body").text
                logger.info(body_text[:1000])  # Primeiros 1000 caracteres
                with open("pagina_texto.txt", "w", encoding="utf-8") as f:
                    f.write(body_text)
                logger.info("\n✓ Texto completo salvo: pagina_texto.txt")
            except Exception as e:
                logger.error(f"Erro ao extrair texto: {e}")

            logger.info("\n" + "=" * 70)
            logger.info("ANÁLISE CONCLUÍDA!")
            logger.info("=" * 70)
            logger.info("Verifique os arquivos gerados para identificar os elementos.")
            logger.info("\nPressione ENTER para fechar...")
            input()

        else:
            logger.error("Falha no login")

    except Exception as e:
        logger.error(f"Erro: {e}")
        import traceback

        logger.error(traceback.format_exc())
    finally:
        scraper.quit()


if __name__ == "__main__":
    analisar_pagina()
