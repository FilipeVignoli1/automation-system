import logging
import sys
import json
import csv
from datetime import datetime
from pathlib import Path
import config.settings as settings


def setup_logging():
    """Configura o sistema de logs"""
    log_filename = f"scraper_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    log_path = Path(settings.LOGS_DIR) / log_filename

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    return logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
    """Remove caracteres inválidos de nomes de arquivo"""
    import re

    return re.sub(r'[<>:"/\\|?*]', "", filename)


def save_data(data, filename_prefix="extracted", format="json"):
    """Salva os dados extraídos em arquivo"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{filename_prefix}_{timestamp}"
    filepath = None

    if format == "json":
        filepath = Path(settings.DATA_DIR) / f"{filename}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    elif format == "csv":
        filepath = Path(settings.DATA_DIR) / f"{filename}.csv"
        # Converte dados aninhados para formato plano se necessário
        flat_data = flatten_data(data)
        if flat_data:
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=flat_data[0].keys(), extrasaction='ignore')
                writer.writeheader()
                writer.writerows(flat_data)

    return filepath


def flatten_data(data):
    """Converte dados aninhados em lista de dicionários planos"""
    if not data:
        return []

    if isinstance(data, dict):
        return [data]

    if isinstance(data, list) and len(data) > 0:
        # Se for lista de dicionários
        if isinstance(data[0], dict):
            return data
        # Se for lista de listas (tabelas)
        elif isinstance(data[0], list):
            return [{f"col_{i}": val for i, val in enumerate(row)} for row in data]

    return [{"data": str(data)}]
