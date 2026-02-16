from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import config.settings as settings
from src.browser import BrowserManager
from src.utils import setup_logging, save_data

logger = setup_logging()


class SiriusScraper:
    """Scraper para o sistema Sirius"""

    def __init__(self, headless=False):
        self.browser = BrowserManager(headless=headless)
        self.driver = None
        self.extracted_data = []

    def start(self):
        """Inicializa o scraper"""
        self.browser.start()
        self.driver = self.browser.driver

    def quit(self):
        """Encerra o scraper"""
        self.browser.quit()

    def login(self):
        """Realiza login no sistema com suporte a 2FA"""
        try:
            logger.info("Acessando página de login...")
            self.driver.get(settings.SIRIUS_URL)

            # Aguarda página carregar
            time.sleep(2)

            # Tenta localizar campos de login (ajustar seletores conforme necessário)
            logger.info("Procurando campos de login...")

            # Exemplo de seletores comuns - AJUSTAR CONFORME A PÁGINA REAL
            try:
                # Tenta encontrar campo de usuário por diferentes métodos
                username_field = (
                    self.driver.find_element(By.NAME, "usuario")
                    or self.driver.find_element(By.NAME, "user")
                    or self.driver.find_element(By.NAME, "login")
                    or self.driver.find_element(By.ID, "usuario")
                    or self.driver.find_element(By.CSS_SELECTOR, "input[type='text']")
                )

                password_field = (
                    self.driver.find_element(By.NAME, "senha")
                    or self.driver.find_element(By.NAME, "password")
                    or self.driver.find_element(By.NAME, "pass")
                    or self.driver.find_element(By.ID, "senha")
                    or self.driver.find_element(
                        By.CSS_SELECTOR, "input[type='password']"
                    )
                )

                # Preenche credenciais
                username_field.clear()
                username_field.send_keys(settings.SIRIUS_USERNAME)
                logger.info("Usuário preenchido")

                password_field.clear()
                password_field.send_keys(settings.SIRIUS_PASSWORD)
                logger.info("Senha preenchida")

                # Clica no botão de login
                login_button = (
                    self.driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                    or self.driver.find_element(By.TAG_NAME, "button")
                    or self.driver.find_element(By.CSS_SELECTOR, ".btn-login")
                )
                login_button.click()

                logger.info("Login enviado, aguardando...")
                time.sleep(2)

                # Verifica se há tela de código 2FA
                if self.handle_2fa():
                    logger.info("Autenticação completa!")
                    time.sleep(2)
                    return True
                else:
                    return False

            except NoSuchElementException as e:
                logger.error(f"Elemento não encontrado: {e}")
                logger.info("Salvando screenshot para debug...")
                self.driver.save_screenshot("login_error.png")
                return False

        except Exception as e:
            logger.error(f"Erro no login: {e}")
            return False

    def handle_2fa(self):
        """Lida com verificação de duas etapas (código)"""
        try:
            # Aguarda um pouco para ver se aparece tela de código ou redirecionamento
            time.sleep(2)

            # Verifica se foi redirecionado para página de validação SMS
            current_url = self.driver.current_url
            if "validacaoSms" in current_url or "validacao" in current_url:
                logger.info("Página de validação SMS detectada!")
                return self._handle_sms_validation()

            # Verifica se há campo de código na página atual
            code_field = None
            possible_selectors = [
                "input[name='codigo']",
                "input[name='code']",
                "input[name='token']",
                "input[name='sms']",
                "input[id='codigo']",
                "input[id='code']",
                "input[type='number']",
                "input[placeholder*='código']",
                "input[placeholder*='code']",
                "input[placeholder*='SMS']",
            ]

            for selector in possible_selectors:
                try:
                    code_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"Campo de código 2FA encontrado: {selector}")
                    break
                except:
                    continue

            if code_field:
                # Verifica se tem código configurado
                if settings.SIRIUS_2FA_CODE:
                    logger.info("Inserindo código 2FA automaticamente...")
                    code_field.clear()
                    code_field.send_keys(settings.SIRIUS_2FA_CODE)

                    # Tenta clicar no botão de confirmar
                    try:
                        submit_button = (
                            self.driver.find_element(
                                By.CSS_SELECTOR, "input[type='submit']"
                            )
                            or self.driver.find_element(By.TAG_NAME, "button")
                            or self.driver.find_element(
                                By.CSS_SELECTOR, ".btn-confirmar"
                            )
                            or self.driver.find_element(
                                By.CSS_SELECTOR, "input[value*='Confirmar']"
                            )
                            or self.driver.find_element(
                                By.CSS_SELECTOR, "input[value*='Enviar']"
                            )
                        )
                        submit_button.click()
                        logger.info("Código enviado!")
                        time.sleep(3)
                    except Exception as btn_error:
                        logger.warning(
                            f"Não foi possível clicar no botão de confirmar: {btn_error}"
                        )
                else:
                    # Modo interativo - aguarda usuário inserir
                    logger.info("=" * 50)
                    logger.info("CÓDIGO DE VERIFICAÇÃO NECESSÁRIO")
                    logger.info("=" * 50)
                    logger.info("Por favor, insira o código no navegador")
                    logger.info("O sistema aguardará 30 segundos...")
                    logger.info("=" * 50)

                    # Aguarda usuário inserir código manualmente
                    time.sleep(30)

                return True
            else:
                # Não há tela de código, login direto
                logger.info("Login direto (sem 2FA)")
                time.sleep(3)
                return True

        except Exception as e:
            logger.warning(f"Erro ao processar 2FA: {e}")
            # Continua mesmo se houver erro no 2FA
            return True

    def _handle_sms_validation(self):
        """Lida especificamente com a página de validação SMS"""
        try:
            logger.info("Processando validação SMS...")

            # Aguarda página carregar completamente
            time.sleep(2)

            # Procura campo de código na página de validação SMS
            code_selectors = [
                "input[name='codigo']",
                "input[name='code']",
                "input[name='token']",
                "input[name='sms']",
                "input[id='codigo']",
                "input[type='text']",
                "input[type='number']",
            ]

            code_field = None
            for selector in code_selectors:
                try:
                    code_field = self.driver.find_element(By.CSS_SELECTOR, selector)
                    logger.info(f"Campo de código encontrado: {selector}")
                    break
                except:
                    continue

            if code_field and settings.SIRIUS_2FA_CODE:
                logger.info(f"Inserindo código: {settings.SIRIUS_2FA_CODE}")
                code_field.clear()
                code_field.send_keys(settings.SIRIUS_2FA_CODE)

                # Procura botão de confirmar
                btn_selectors = [
                    "input[type='submit']",
                    "button[type='submit']",
                    "button",
                    "input[value*='Confirmar']",
                    "input[value*='Enviar']",
                    "input[value*='Validar']",
                    ".btn-confirmar",
                    "#btn-confirmar",
                ]

                for btn_selector in btn_selectors:
                    try:
                        submit_btn = self.driver.find_element(
                            By.CSS_SELECTOR, btn_selector
                        )
                        submit_btn.click()
                        logger.info("Código confirmado na página de validação SMS!")
                        time.sleep(3)
                        return True
                    except:
                        continue

                logger.warning("Botão de confirmar não encontrado automaticamente")
                time.sleep(5)  # Aguarda usuário clicar manualmente
                return True
            else:
                logger.info("Aguardando inserção manual do código...")
                time.sleep(30)
                return True

        except Exception as e:
            logger.error(f"Erro na validação SMS: {e}")
            return True

    def switch_to_frame(self, frame_name=None):
        """Muda para um frame específico ou volta ao conteúdo principal"""
        try:
            if frame_name:
                self.driver.switch_to.frame(frame_name)
                logger.info(f"Mudado para frame: {frame_name}")
            else:
                self.driver.switch_to.default_content()
                logger.info("Voltado ao conteúdo principal")
            return True
        except Exception as e:
            logger.warning(f"Erro ao mudar de frame: {e}")
            return False

    def navigate_to_workflow(self):
        """Navega para a opção Workflow"""
        try:
            logger.info("Navegando para Workflow...")

            # O botão Workflow está no frame 'baixo' e é uma imagem
            try:
                self.switch_to_frame("baixo")
                
                # Seletores baseados no dump HTML (imagem com onclick)
                workflow_selectors = [
                    "img[src*='workflow.png']",
                    "img[onclick*='workflow.csp']",
                    "img[src*='Workflow']",
                    "a[href*='workflow']", # Mantendo backup
                ]

                for selector in workflow_selectors:
                    try:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        # O elemento é uma imagem com onclick, então clicamos nela
                        element.click()
                        logger.info(f"Workflow clicado via seletor: {selector}")
                        
                        # Aguarda navegação
                        time.sleep(5)
                        
                        # Volta ao contexto principal para lidar com a nova página
                        self.switch_to_frame(None)
                        return True
                    except:
                        continue
                
                logger.warning("Seletores de imagem falharam, tentando acesso direto URL...")

            except Exception as frame_error:
                logger.warning(f"Erro ao interagir no frame baixo: {frame_error}")
                self.switch_to_frame(None)

            # Fallback: Tenta acesso direto via URL construída
            # Nota: O URL pode depender da sessão, mas o dump mostrou 'usuario=VIGNOLI'
            try:
                workflow_url = "https://sirius.assim.com.br/assimcsp/wflow/workflow.csp?usuario=VIGNOLI"
                self.driver.get(workflow_url)
                logger.info(f"Tentativa de acesso direto: {workflow_url}")
                time.sleep(3)
                return True
            except Exception as e:
                logger.error(f"Falha no acesso direto: {e}")

            logger.error("Não foi possível encontrar o menu Workflow")
            self.driver.save_screenshot("workflow_not_found.png")
            return False

        except Exception as e:
            logger.error(f"Erro ao navegar para Workflow: {e}")
            return False

    def navigate_to_painel(self):
        """Navega para a opção Painel dentro do Workflow"""
        try:
            logger.info("Navegando para Painel...")
            
            # Tenta encontrar no frame principal, topo ou baixo
            # Como não sabemos a estrutura da pág Workflow ainda, tentamos genericamente
            
            frames_to_try = [None, "cima", "baixo", "topo"]
            
            for frame in frames_to_try:
                try:
                    if frame:
                        self.switch_to_frame(frame)
                    
                    # Seletores para Painel
                    painel_selectors = [
                        "a[href*='painel']",
                        "a[href*='Painel']",
                        "//a[contains(text(), 'Painel')]",
                        "//span[contains(text(), 'Painel')]",
                        "img[src*='painel']",
                        "img[title*='Painel']"
                    ]
                    
                    for selector in painel_selectors:
                        try:
                            if selector.startswith("//"):
                                element = self.driver.find_element(By.XPATH, selector)
                            else:
                                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                
                            element.click()
                            logger.info(f"Painel clicado (Frame: {frame}, Seletor: {selector})")
                            time.sleep(3)
                            self.switch_to_frame(None)
                            return True
                        except:
                            continue
                            
                    if frame:
                        self.switch_to_frame(None)
                        
                except Exception as frame_e:
                    logger.warning(f"Erro ao buscar Painel no frame {frame}: {frame_e}")
                    self.switch_to_frame(None)

            # Se falhar, salva debug da página Workflow
            logger.error("Painel não encontrado. Salvando debug...")
            self.driver.save_screenshot("painel_not_found.png")
            with open("workflow_page_dump.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            logger.info("Dump da página Workflow salvo em workflow_page_dump.html")
            
            return False

        except Exception as e:
            logger.error(f"Erro ao navegar para Painel: {e}")
            return False

    def _normalize_table_data(self, table_data):
        """
        Normaliza dados de tabela, tratando casos de tabelas verticais 
        onde cada célula contém a coluna inteira separada por quebras de linha.
        """
        if not table_data or len(table_data) > 3:  # Se tem muitas linhas, provavelmente já está ok
            return table_data

        # Verifica se a primeira linha tem células com muitas quebras de linha
        first_row = table_data[0]
        multiline_cells = sum(1 for cell in first_row if isinstance(cell, str) and '\n' in cell)
        
        # Se mais da metade das células tem quebras de linha, ou se tem poucas linhas mas conteúdo extenso
        if multiline_cells > len(first_row) / 2 or (len(table_data) == 1 and multiline_cells > 0):
            logger.info("Detectada tabela vertical/transposta. Normalizando...")
            
            # Divide cada célula em uma lista de valores
            columns = []
            max_rows = 0
            
            for cell in first_row:
                if isinstance(cell, str):
                    values = [v.strip() for v in cell.split('\n')]
                    columns.append(values)
                    max_rows = max(max_rows, len(values))
                else:
                    columns.append([str(cell)])
                    
            # Reconstrói a tabela transpondo as colunas para linhas
            normalized_data = []
            for i in range(max_rows):
                new_row = []
                for col in columns:
                    if i < len(col):
                        new_row.append(col[i])
                    else:
                        new_row.append("") # Preenchimento para colunas menores
                normalized_data.append(new_row)
                
            logger.info(f"Tabela normalizada: {len(normalized_data)} linhas encontradas.")
            return normalized_data
            
        return table_data

    def extract_table_data(self, table_selector=None):
        """Extrai dados de tabelas"""
        try:
            logger.info("Extraindo dados de tabelas...")

            # Seletor padrão para tabelas (ajustar conforme necessário)
            if not table_selector:
                table_selector = "table"

            tables = self.driver.find_elements(By.CSS_SELECTOR, table_selector)
            data = []

            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                table_data = []

                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td") or row.find_elements(
                        By.TAG_NAME, "th"
                    )
                    row_data = [cell.text.strip() for cell in cells]
                    if row_data:
                        table_data.append(row_data)

                if table_data:
                    # Aplica normalização
                    normalized = self._normalize_table_data(table_data)
                    data.append(normalized)

            logger.info(f"Extraídas {len(data)} tabelas")
            return data

        except Exception as e:
            logger.error(f"Erro ao extrair tabela: {e}")
            return []

    def extract_workflow_data(self):
        """Extrai dados específicos do Workflow"""
        try:
            logger.info("Extraindo dados do Workflow...")
            time.sleep(2)

            workflow_data = {
                "url": self.driver.current_url,
                "title": self.driver.title,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "cards": [],
                "lists": [],
                "tables": [],
                "forms": [],
                "panels": [],
                "raw_text": "",
            }

            # Verifica se há frames e muda para o frame de conteúdo (baixo)
            try:
                self.switch_to_frame("baixo")
                logger.info("Mudado para frame 'baixo' para extração")
            except:
                logger.info("Sem frame 'baixo', continuando no conteúdo atual")

            # 1. Extrair cards (cartões de workflow)
            card_selectors = [
                ".card",
                ".workflow-card",
                ".task-card",
                ".process-card",
                "[class*='card']",
                "[class*='workflow']",
                ".kanban-card",
                ".task-item",
                ".process-item",
            ]

            for selector in card_selectors:
                try:
                    cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for card in cards:
                        try:
                            card_text = card.text.strip()
                            if card_text and len(card_text) > 5:
                                card_info = {
                                    "type": "card",
                                    "selector": selector,
                                    "content": card_text,
                                    "html": card.get_attribute("outerHTML")[:500],
                                }
                                workflow_data["cards"].append(card_info)
                        except:
                            pass
                except:
                    pass

            # 2. Extrair listas (ul/ol)
            try:
                lists = self.driver.find_elements(By.CSS_SELECTOR, "ul, ol")
                for lst in lists:
                    try:
                        items = lst.find_elements(By.TAG_NAME, "li")
                        if items:
                            list_data = {
                                "type": "list",
                                "item_count": len(items),
                                "items": [
                                    item.text.strip()
                                    for item in items
                                    if item.text.strip()
                                ],
                            }
                            if list_data["items"]:
                                workflow_data["lists"].append(list_data)
                    except:
                        pass
            except:
                pass

            # 3. Extrair tabelas com estrutura específica de workflow
            try:
                tables = self.driver.find_elements(
                    By.CSS_SELECTOR, "table, .dataTable, .workflow-table"
                )
                for table in tables:
                    try:
                        rows = table.find_elements(By.TAG_NAME, "tr")
                        if rows:
                            table_data = []
                            headers = []

                            # Extrair headers
                            header_cells = rows[0].find_elements(By.TAG_NAME, "th")
                            if header_cells:
                                headers = [cell.text.strip() for cell in header_cells]

                            # Extrair dados das linhas
                            for row in rows[1:] if headers else rows:
                                cells = row.find_elements(By.TAG_NAME, "td")
                                if cells:
                                    if headers:
                                        row_dict = {
                                            headers[i]: cell.text.strip()
                                            for i, cell in enumerate(cells)
                                            if i < len(headers)
                                        }
                                    else:
                                        row_dict = {
                                            f"col_{i}": cell.text.strip()
                                            for i, cell in enumerate(cells)
                                        }
                                    if any(row_dict.values()):
                                        table_data.append(row_dict)

                            if table_data:
                                # Normaliza também para Workflow (caso venha como dicts, converte ou trata)
                                # A normalização atual espera lista de listas strings.
                                # Se table_data é lista de dicts, _normalize pode falhar se não adaptada.
                                # Mas para tabelas verticais, geralmente extract_workflow_data falha em detectar headers
                                # e cai no 'else' sem headers? 
                                # Se cair no else (col_i), é lista de dicts.
                                # Vamos converter pra lista de listas para normalizar, depois voltar pra dict?
                                # Simplificação: Se detectarmos tabela vertical aqui, ela provavelmente veio sem headers 
                                # e virou {'col_0': 'Matricula\n...'}
                                
                                # Verifica se é caso de normalização
                                if len(table_data) == 1 and any('\n' in str(v) for v in table_data[0].values()):
                                     # Converte para lista de listas
                                     list_data = [list(table_data[0].values())]
                                     normalized = self._normalize_table_data(list_data)
                                     
                                     # Reconverte para dicts assumindo primeira linha como header
                                     if normalized and len(normalized) > 1:
                                         headers = normalized[0]
                                         new_table_data = []
                                         for row in normalized[1:]:
                                             new_row = {headers[i]: row[i] for i in range(len(headers)) if i < len(row)}
                                             new_table_data.append(new_row)
                                         workflow_data["tables"].append(new_table_data)
                                     else:
                                         workflow_data["tables"].append(table_data)
                                else:
                                    workflow_data["tables"].append(table_data)
                    except:
                        pass
            except:
                pass

            # 4. Extrair formulários
            try:
                forms = self.driver.find_elements(By.CSS_SELECTOR, "form")
                for form in forms:
                    try:
                        inputs = form.find_elements(
                            By.CSS_SELECTOR, "input, select, textarea"
                        )
                        form_data = {
                            "type": "form",
                            "input_count": len(inputs),
                            "fields": [],
                        }
                        for inp in inputs:
                            try:
                                field_info = {
                                    "type": inp.get_attribute("type") or inp.tag_name,
                                    "name": inp.get_attribute("name"),
                                    "id": inp.get_attribute("id"),
                                    "value": inp.get_attribute("value"),
                                    "placeholder": inp.get_attribute("placeholder"),
                                }
                                form_data["fields"].append(field_info)
                            except:
                                pass
                        if form_data["fields"]:
                            workflow_data["forms"].append(form_data)
                    except:
                        pass
            except:
                pass

            # 5. Extrair painéis/divs com conteúdo estruturado
            panel_selectors = [
                ".panel",
                ".panel-body",
                ".widget",
                ".dashboard-widget",
                ".info-box",
                ".stat-box",
                ".status-panel",
            ]

            for selector in panel_selectors:
                try:
                    panels = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for panel in panels:
                        try:
                            panel_text = panel.text.strip()
                            if panel_text and len(panel_text) > 10:
                                panel_data = {
                                    "type": "panel",
                                    "selector": selector,
                                    "content": panel_text,
                                }
                                workflow_data["panels"].append(panel_data)
                        except:
                            pass
                except:
                    pass

            # 6. Extrair todo o texto visível
            try:
                workflow_data["raw_text"] = self.driver.find_element(
                    By.TAG_NAME, "body"
                ).text
            except:
                pass

            logger.info(f"Extraídos do Workflow:")
            logger.info(f"  - {len(workflow_data['cards'])} cards")
            logger.info(f"  - {len(workflow_data['lists'])} listas")
            logger.info(f"  - {len(workflow_data['tables'])} tabelas")
            logger.info(f"  - {len(workflow_data['forms'])} formulários")
            logger.info(f"  - {len(workflow_data['panels'])} painéis")

            # Volta ao frame principal
            try:
                self.switch_to_frame(None)
            except:
                pass

            return workflow_data

        except Exception as e:
            logger.error(f"Erro ao extrair dados do Workflow: {e}")
            # Tenta voltar ao frame principal em caso de erro
            try:
                self.switch_to_frame(None)
            except:
                pass
            return {}

    def extract_all_data(self, is_workflow=False):
        """Extrai todos os dados disponíveis na página atual"""
        try:
            logger.info("Extraindo todos os dados da página...")

            if is_workflow or "workflow" in self.driver.current_url.lower():
                # Usa extração específica do workflow
                data = self.extract_workflow_data()
            else:
                # Tenta mudar para frame "baixo" se existir
                try:
                    self.switch_to_frame("baixo")
                    in_frame = True
                except:
                    in_frame = False

                # Extração genérica
                data = {
                    "url": self.driver.current_url,
                    "title": self.driver.title,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "tables": self.extract_table_data(),
                    "text_content": self.driver.find_element(By.TAG_NAME, "body").text,
                }

                # Volta ao frame principal se estava em um frame
                if in_frame:
                    try:
                        self.switch_to_frame(None)
                    except:
                        pass

            self.extracted_data.append(data)
            logger.info("Dados extraídos com sucesso!")
            return data

        except Exception as e:
            logger.error(f"Erro ao extrair dados: {e}")
            # Tenta voltar ao frame principal em caso de erro
            try:
                self.switch_to_frame(None)
            except:
                pass
            return {}

    def save(self, format="json"):
        """Salva os dados extraídos"""
        if self.extracted_data:
            filepath = save_data(self.extracted_data, format=format)
            logger.info(f"Dados salvos em: {filepath}")
            return filepath
        else:
            logger.warning("Nenhum dado para salvar")
            return None

    def save_tables(self):
        """Salva tabelas extraídas em CSVs separados"""
        import csv
        from pathlib import Path
        
        saved_count = 0
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        
        for i, page_data in enumerate(self.extracted_data):
            if "tables" in page_data and page_data["tables"]:
                for j, table in enumerate(page_data["tables"]):
                    # Ignora tabelas muito pequenas (menos de 2 linhas)
                    if len(table) < 2:
                        continue
                        
                    filename = f"tabela_{timestamp}_p{i}_t{j}.csv"
                    filepath = Path(settings.DATA_DIR) / filename
                    
                    try:
                        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                            # Verifica se é lista de dicts ou lista de listas
                            if len(table) > 0 and isinstance(table[0], dict):
                                fields = table[0].keys()
                                writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
                                writer.writeheader()
                                writer.writerows(table)
                            else:
                                writer = csv.writer(f)
                                writer.writerows(table)
                                
                        logger.info(f"Tabela salva: {filename}")
                        saved_count += 1
                    except Exception as e:
                        logger.error(f"Erro ao salvar tabela {filename}: {e}")

    def run_full_extraction(self, headless=False, workflow=True, painel=True):
        """Executa extração completa navegando por Workflow e Painel"""
        try:
            self.start()

            if self.login():
                logger.info("Login bem-sucedido! Iniciando extração...")

                # Extrai dados da página inicial
                logger.info("Extraindo dados da página inicial...")
                self.extract_all_data()

                # Navega para Workflow se solicitado OU se precisar ir ao Painel
                if workflow or painel:
                    logger.info("=" * 50)
                    logger.info("NAVEGANDO PARA WORKFLOW")
                    logger.info("=" * 50)
                    
                    if self.navigate_to_workflow():
                        logger.info("Extraindo dados do Workflow...")
                        self.extract_all_data(is_workflow=True)
                        
                        # Se painel foi solicitado, navega agora
                        if painel:
                            logger.info("=" * 50)
                            logger.info("NAVEGANDO PARA PAINEL")
                            logger.info("=" * 50)
                            if self.navigate_to_painel():
                                logger.info("Extraindo dados do Painel...")
                                
                                # DEBUG: Salvar HTML para verificar paginação
                                with open("debug_painel.html", "w", encoding="utf-8") as f:
                                    f.write(self.driver.page_source)
                                    
                                # Força is_workflow=True para usar a lógica de extração melhorada (headers, dicts)
                                self.extract_all_data(is_workflow=True)
                            else:
                                logger.warning("Não foi possível acessar o Painel")
                    else:
                        logger.warning("Não foi possível acessar o Workflow (abortando Painel)")

                # Salva todos os dados extraídos
                logger.info("=" * 50)
                logger.info("SALVANDO DADOS")
                logger.info("=" * 50)
                self.save(format="json")
                self.save(format="csv")
                self.save_tables()

                logger.info("Extração completa finalizada!")
            else:
                logger.error("Falha no login. Verifique as credenciais.")

        except Exception as e:
            logger.error(f"Erro durante extração: {e}")
        finally:
            self.quit()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()
