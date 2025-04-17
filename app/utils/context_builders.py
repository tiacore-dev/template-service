from collections import defaultdict
import datetime
from loguru import logger


def format_date(value: str) -> str:
    logger.debug(f"[format_date] Получено: {value} ({type(value)})")
    try:
        if isinstance(value, (int, float)):
            dt = datetime.datetime.fromtimestamp(float(value))
        elif isinstance(value, str):
            try:
                dt = datetime.datetime.fromisoformat(value)
            except ValueError:
                dt = datetime.datetime.strptime(value, "%Y-%m-%d")
        else:
            raise ValueError("Неподдерживаемый тип")
        logger.debug(f"[format_date] timestamp: {dt}")
        return dt.strftime("%d.%m.%Y")
    except Exception as e:
        logger.error(f"[format_date] Ошибка при форматировании: {value}: {e}")
        return value


def flatten_context(obj, parent_key='', sep='.') -> dict:
    """
    Рекурсивно разворачивает вложенные dict и списки в плоский словарь:
    {
        "act.details.0.service.service_name": "Имя услуги",
        ...
    }
    """
    items = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.update(flatten_context(v, new_key, sep=sep))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.update(flatten_context(v, new_key, sep=sep))
    else:
        items[parent_key] = obj
    return items


def deep_defaultdict(value=None):
    if isinstance(value, dict):
        return defaultdict(lambda: "-", {k: deep_defaultdict(v) for k, v in value.items()})
    elif isinstance(value, list):
        return [deep_defaultdict(v) for v in value]
    return value
