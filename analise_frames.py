#!/usr/bin/env python3
"""
Análise dos frames do Sirius
Descobre os links corretos de Workflow e Painel
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


def analisar_frames():
    """Analisa os frames da página Sirius"""

    scraper = SiriusScraper(headless=False)

    try:
        scraper.start()

        if scraper.login():
            logger.info("=" * 70)
            logger.info("ANÁLISE DE FRAMES")
            logger.info("=" * 70)

            time.sleep(3)

            # Analisa frame "cima" (menu)
            logger.info("\n" + "=" * 70)
            logger.info("FRAME 'CIMA' - MENU SUPERIOR")
            logger.info("=" * 70)

            try:
                scraper.switch_to_frame("cima")
                scraper.driver.save_screenshot("frame_cima.png")
                logger.info("Screenshot do frame 'cima' salvo: frame_cima.png")

                # Extrai todos os links
                links = scraper.driver.find_elements(By.TAG_NAME, "a")
                logger.info(f"\nTotal de links no menu: {len(links)}")

                menu_links = []
                for i, link in enumerate(links, 1):
                    try:
                        texto = link.text.strip()
                        href = link.get_attribute("href")
                        onclick = link.get_attribute("onclick")

                        if texto or href or onclick:
                            logger.info(f"\n{i}. Texto: '{texto}'")
                            logger.info(f"   href: {href}")
                            logger.info(f"   onclick: {onclick}")
                            menu_links.append(
                                {"texto": texto, "href": href, "onclick": onclick}
                            )
                    except:
                        pass

                # Salva links do menu
                with open("menu_links.json", "w", encoding="utf-8") as f:
                    json.dump(menu_links, f, indent=2, ensure_ascii=False)
                logger.info("\nLinks do menu salvos: menu_links.json")

            except Exception as e:
                logger.error(f"Erro ao analisar frame 'cima': {e}")

            # Volta ao principal
            scraper.switch_to_frame(None)

            # Analisa frame "baixo" (conteúdo)
            logger.info("\n" + "=" * 70)
            logger.info("FRAME 'BAIXO' - CONTEÚDO PRINCIPAL")
            logger.info("=" * 70)

            try:
                scraper.switch_to_frame("baixo")
                scraper.driver.save_screenshot("frame_baixo.png")
                logger.info("Screenshot do frame 'baixo' salvo: frame_baixo.png")

                # Extrai URL atual
                current_url = scraper.driver.current_url
                logger.info(f"\nURL atual: {current_url}")

                # Extrai HTML
                html = scraper.driver.page_source
                with open("frame_baixo.html", "w", encoding="utf-8") as f:
                    f.write(html[:5000])  # Primeiros 5000 caracteres
                logger.info("HTML do frame 'baixo' salvo: frame_baixo.html")

                # Extrai texto
                try:
                    body_text = scraper.driver.find_element(By.TAG_NAME, "body").text
                    logger.info(f"\nTexto do frame:\n{body_text[:500]}")
                    with open("frame_baixo_texto.txt", "w", encoding="utf-8") as f:
                        f.write(body_text)
                    logger.info("Texto completo salvo: frame_baixo_texto.txt")
                except:
                    pass

                # Extrai links
                links = scraper.driver.find_elements(By.TAG_NAME, "a")
                logger.info(f"\nTotal de links no conteúdo: {len(links)}")

                for i, link in enumerate(links[:10], 1):  # Primeiros 10
                    try:
                        texto = link.text.strip()
                        href = link.get_attribute("href")
                        if texto:
                            logger.info(f"{i}. '{texto}' -> {href}")
                    except:
                        pass

            except Exception as e:
                logger.error(f"Erro ao analisar frame 'baixo': {e}")

            # Volta ao principal
            scraper.switch_to_frame(None)

            logger.info("\n" + "=" * 70)
            logger.info("ANÁLISE CONCLUÍDA!")
            logger.info("=" * 70)
            logger.info("\nVerifique os arquivos gerados para identificar:")
            logger.info("- menu_links.json (links do menu)")
            logger.info("- frame_cima.png (screenshot do menu)")
            logger.info("- frame_baixo.html (HTML do conteúdo)")

        else:
            logger.error("Falha no login")

    except Exception as e:
        logger.error(f"Erro: {e}")
        import traceback

        logger.error(traceback.format_exc())
    finally:
        scraper.quit()
        logger.info("\nNavegador fechado.")


if __name__ == "__main__":
    analisar_frames()
