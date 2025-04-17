from io import BytesIO
import os
from zipfile import is_zipfile
from urllib.parse import quote
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from loguru import logger
from app.pydantic_models.doc_schemas import GenerateSchema
from app.handlers.template_handler import handle_docs
from app.utils.converter import convert_to_pdf
from app.s3.s3_manager import AsyncS3Manager

doc_router = APIRouter()


MEDIA_TYPES = {
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pdf": "application/pdf"
}


@doc_router.post("/generate", response_class=StreamingResponse)
async def generate_file(data: GenerateSchema):
    logger.info(
        f"Запрос на генерацию файла: name={data.name}, s3_key={data.s3_key}, is_pdf={data.is_pdf}")

    manager = AsyncS3Manager()

    try:
        template_bytes = await manager.download_bytes(data.s3_key)
        if not is_zipfile(BytesIO(template_bytes)):
            logger.error(
                f"Файл по ключу {data.s3_key} не является zip-файлом. Начало файла: {template_bytes[:20]}")
            raise ValueError("Файл не является корректным DOCX (zip) файлом.")
        logger.debug(f"Шаблон успешно загружен с S3: {data.s3_key}")
    except Exception as e:
        logger.exception(
            f"Ошибка при загрузке шаблона с S3: {data.s3_key}. Ошибка: {e}")
        raise

    extension = os.path.splitext(data.s3_key)[-1].lower().replace('.', '')

    try:
        document_bytes = await handle_docs(data.document_data, template_bytes, extension)
        logger.info(f"Документ сгенерирован: формат={extension}")
    except Exception as e:
        logger.exception(f"Ошибка при генерации документа: {e}")
        raise

    if data.is_pdf:
        try:
            document_bytes = convert_to_pdf(document_bytes, extension)
            extension = "pdf"
            logger.info("Документ успешно сконвертирован в PDF")
        except Exception as e:
            logger.exception("Ошибка при конвертации в PDF")
            raise

    media_type = MEDIA_TYPES.get(extension, "application/octet-stream")
    safe_name = Path(data.name).name.replace('"', '').replace("'", '')
    filename = f"{safe_name}.{extension}"

    logger.info(f"Отправка файла клиенту: {filename}, media_type={media_type}")

    disposition = f"attachment; filename*=UTF-8''{quote(filename)}"

    return StreamingResponse(
        BytesIO(document_bytes),
        media_type=media_type,
        headers={"Content-Disposition": disposition}
    )
