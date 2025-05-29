from io import BytesIO
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger

from app.exceptions import InvalidTemplateError
from app.handlers.get_content import load_input_file
from app.handlers.template_handler import handle_docs
from app.pydantic_models.doc_schemas import GenerateSchema
from app.utils.converter import convert_to_pdf

doc_router = APIRouter()


MEDIA_TYPES = {
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pdf": "application/pdf",
}


@doc_router.post("/generate", response_class=StreamingResponse)
async def generate_file(data: GenerateSchema):
    logger.debug(f"[load_input_file] Загрузка URL: {data.url}")

    file_bytes, filename, extension = await load_input_file(data)

    try:
        document_bytes = await handle_docs(data.document_data, file_bytes, extension)
        logger.info(f"Документ сгенерирован: формат={extension}")
    except InvalidTemplateError as e:
        logger.warning(f"Неверный шаблон или данные: {e.message}")
        raise HTTPException(status_code=400, detail=e.message) from e

    if data.is_pdf:
        try:
            document_bytes = convert_to_pdf(document_bytes, extension)
            extension = "pdf"
            logger.info("Документ успешно сконвертирован в PDF")
        except Exception:
            logger.exception("Ошибка при конвертации в PDF")
            raise

    media_type = MEDIA_TYPES.get(extension, "application/octet-stream")
    safe_name = Path(data.name).name.replace('"', "").replace("'", "")
    filename = f"{safe_name}.{extension}"

    logger.info(f"Отправка файла клиенту: {filename}, media_type={media_type}")

    disposition = f"attachment; filename*=UTF-8''{quote(filename)}"

    return StreamingResponse(
        BytesIO(document_bytes),
        media_type=media_type,
        headers={"Content-Disposition": disposition},
    )
