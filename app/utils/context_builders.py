import datetime


def format_date(value) -> str:
    try:
        if isinstance(value, str):
            try:
                # если ISO-строка
                dt = datetime.datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                # если ISO с временем
                dt = datetime.datetime.fromisoformat(value)
        elif isinstance(value, (int, float)):
            dt = datetime.datetime.fromtimestamp(value)
        else:
            return "–"

        return dt.strftime("%d.%m.%Y")
    except Exception:
        return "–"


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
