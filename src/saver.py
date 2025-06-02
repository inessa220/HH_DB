import json
import os
from typing import Dict, List, Union, Optional
from dotenv import load_dotenv

load_dotenv()


def connection() -> Dict[str, Optional[str]]:
    """Возвращает словарь с параметрами для подключения к базе данных PostgreSQL"""
    return {
        "host": os.getenv("host"),
        "port": os.getenv("port"),
        "user": os.getenv("user"),
        "password": os.getenv("password"),
    }


def save_companies_to_file(companies: list, filename: str) -> None:
    """Сохраняет список компаний в файл JSON"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(companies, f, ensure_ascii=False, indent=4)
        print(f"Данные о компаниях успешно сохранены в файл '{filename}'.")
    except OSError as e:
        print(f"Ошибка при записи в файл: {e}")


def load_companies_from_file(filename: str) -> List[Dict[str, Union[str, int, bool]]]:
    """Загружает список компаний из файла JSON"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Файл '{filename}' не найден.")
        return []
    except json.JSONDecodeError:
        print(f"Ошибка при чтении файла '{filename}': неверный формат JSON.")
        return []
    except IOError as e:
        print(f"Ошибка при чтении файла: {e}")
        return []
