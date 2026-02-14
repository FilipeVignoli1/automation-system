#!/usr/bin/env python3
"""
Script de diagnóstico avançado - Análise completa da página
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.scraper import SiriusScraper
from src.utils import setup_logging

logger = setup_logging()


def advanced_diagnosis():
    """Diagnóstico completo da estrutura da página"""

    scraper = SiriusScraper(headless=False)

    try:
        scraper.start()

        if scraper.login():
            logger.info("=" * 70)
            logger.info("DIAGNÓSTICO AVANÇADO")
            logger.info("=" * 70)
            logger.info("Aguardando carregamento completo...")
            time.sleep(5)  # Aguarda mais tempo

            # Screenshot
            scraper.driver.save_screenshot("diagnostico_avancado.png")
            logger.info("Screenshot salvo: diagnostico_avancado.png")

            # Verifica iframes
            logger.info("\n" + "=" * 70)
            logger.info("IFRAMES ENCONTRADOS:")
            logger.info("=" * 70)
            iframes = scraper.driver.find_elements(By.TAG_NAME, "iframe")
            logger.info(f"Total de iframes: {len(iframes)}")
            for i, iframe in enumerate(iframes):
                try:
                    name = iframe.get_attribute("name") or "sem nome"
                    id_attr = iframe.get_attribute("id") or "sem id"
                    src = iframe.get_attribute("src") or "sem src"
                    logger.info(
                        f"{i + 1}. ID: {id_attr} | Name: {name} | Src: {src[:50]}"
                    )
                except:
                    pass

            # Se houver iframes, analisa o primeiro
            if len(iframes) > 0:
                logger.info("\nTrocando para iframe 0...")
                scraper.driver.switch_to.frame(iframes[0])
                time.sleep(2)

            # Lista TODOS os elementos visíveis
            logger.info("\n" + "=" * 70)
            logger.info("TODOS OS ELEMENTOS CLICÁVEIS:")
            logger.info("=" * 70)

            # Procura por divs, spans, e outros elementos com evento de clique
            clickable_selectors = [
                "div[onclick]",
                "span[onclick]",
                "div[role='button']",
                "span[role='button']",
                "[class*='menu']",
                "[class*='nav']",
                "[class*='btn']",
                "[class*='button']",
                "[class*='link']",
                "div",
                "span",
                "li",
                "td",
            ]

            elementos_encontrados = []

            for selector in clickable_selectors:
                try:
                    elements = scraper.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements[:30]:  # Limita a 30 por tipo
                        try:
                            texto = elem.text.strip()
                            if (
                                texto and len(texto) < 100
                            ):  # Só elementos com texto curto
                                tag = elem.tag_name
                                classe = elem.get_attribute("class") or ""
                                id_attr = elem.get_attribute("id") or ""
                                onclick = elem.get_attribute("onclick") or ""

                                # Filtra elementos relevantes
                                if any(
                                    palavra in texto.lower()
                                    for palavra in [
                                        "workflow",
                                        "painel",
                                        "dash",
                                        "board",
                                        "trabalho",
                                        "fluxo",
                                        "processo",
                                        "work",
                                        "inicio",
                                        "home",
                                    ]
                                ):
                                    elementos_encontrados.append(
                                        {
                                            "tag": tag,
                                            "texto": texto,
                                            "classe": classe[:50],
                                            "id": id_attr,
                                            "onclick": onclick[:50],
                                            "seletor": f"{tag}[class='{classe}']"
                                            if classe
                                            else f"{tag}:contains('{texto}')",
                                        }
                                    )
                        except:
                            pass
                except:
                    pass

            # Remove duplicados
            elementos_unicos = []
            textos_vistos = set()
            for elem in elementos_encontrados:
                if elem["texto"] not in textos_vistos:
                    elementos_unicos.append(elem)
                    textos_vistos.add(elem["texto"])

            # Exibe resultados
            for i, elem in enumerate(elementos_unicos[:20], 1):
                logger.info(f"\n{i}. Texto: '{elem['texto']}'")
                logger.info(f"   Tag: {elem['tag']}")
                logger.info(f"   Classe: {elem['classe']}")
                logger.info(f"   ID: {elem['id']}")
                if elem["onclick"]:
                    logger.info(f"   OnClick: {elem['onclick']}")
                logger.info(f"   Sugestão seletor: {elem['seletor']}")

            # Salva em JSON para análise
            with open("elementos_encontrados.json", "w", encoding="utf-8") as f:
                json.dump(elementos_unicos, f, ensure_ascii=False, indent=2)
            logger.info(f"\nElementos salvos em: elementos_encontrados.json")

            # Captura HTML da página
            html = scraper.driver.page_source
            with open("pagina_html.html", "w", encoding="utf-8") as f:
                f.write(html[:50000])  # Primeiros 50k caracteres
            logger.info("HTML salvo em: pagina_html.html")

            logger.info("\n" + "=" * 70)
            logger.info("DIAGNÓSTICO AVANÇADO CONCLUÍDO!")
            logger.info("=" * 70)
            logger.info("\nVerifique os arquivos gerados:")
            logger.info("1. diagnostico_avancado.png - Screenshot")
            logger.info("2. elementos_encontrados.json - Elementos em JSON")
            logger.info("3. pagina_html.html - HTML da página")
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
    advanced_diagnosis()
