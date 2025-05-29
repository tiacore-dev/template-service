from collections import defaultdict
from io import BytesIO
from typing import Any, Dict

from docxtpl import DocxTemplate
from loguru import logger
from xlsxtpl.writerx import BookWriter

from app.exceptions import InvalidTemplateError
from app.utils.context_builders import deep_defaultdict, format_date


def preprocess_dates(context: Any) -> Any:
    def format_value(key, val):
        if isinstance(val, (dict, list)):
            return preprocess_dates(val)
        if isinstance(key, str) and "date" in key.lower():
            return format_date(val)
        return val

    if isinstance(context, dict):
        return {k: format_value(k, v) for k, v in context.items()}
    elif isinstance(context, list):
        return [preprocess_dates(item) for item in context]
    return context


def deep_to_dict(obj: Any) -> Any:
    if isinstance(obj, defaultdict):
        return {k: deep_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, dict):
        return {k: deep_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [deep_to_dict(i) for i in obj]
    else:
        return obj


async def handle_docs(data: dict, template_bytes: bytes, extention: str) -> bytes:
    try:
        logger.debug(f"[handle_docs] Обработка шаблона: .{extention}")
        prepared_data = preprocess_dates(data)
        context = deep_to_dict(deep_defaultdict(prepared_data))
        # ⬅️ здесь приведение к dict

        if extention == "docx":
            return generate_docx_from_bytes(template_bytes, context)
        elif extention == "xlsx":
            return generate_excel_from_template_with_bookwriter(template_bytes, context)
        else:
            raise InvalidTemplateError(f"Неподдерживаемое расширение: {extention}")
    except InvalidTemplateError:
        raise
    except Exception as e:
        logger.exception(f"[handle_docs] Ошибка при генерации документа: {e}")
        raise InvalidTemplateError("Ошибка при обработке шаблона или данных") from e


def generate_docx_from_bytes(template_bytes: bytes, context: Dict[str, Any]) -> bytes:
    try:
        doc_stream = BytesIO(template_bytes)
        doc = DocxTemplate(doc_stream)

        logger.debug("[generate_docx_from_bytes] Рендер docx шаблона")
        doc.render(context)

        output_stream = BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)
        return output_stream.read()
    except Exception as e:
        logger.exception(f"[generate_docx_from_bytes] Ошибка при рендеринге .docx: {e}")
        raise InvalidTemplateError("Некорректный шаблон или неподходящие данные") from e


def generate_excel_from_template_with_bookwriter(
    template_bytes: bytes, context: Dict[str, Any]
) -> bytes:
    try:
        input_stream = BytesIO(template_bytes)
        output_stream = BytesIO()

        writer = BookWriter(input_stream)
        writer.render_sheet(context)
        writer.save(output_stream)

        output_stream.seek(0)
        return output_stream.read()

    except Exception:
        import logging

        logging.exception("Ошибка при генерации xlsx через BookWriter")
        return b""
