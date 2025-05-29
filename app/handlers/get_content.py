import os
from pathlib import Path
from urllib.parse import urlparse

import aiohttp
from loguru import logger

from app.pydantic_models.doc_schemas import GenerateSchema

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"


async def download_with_aiohttp_strict(url: str) -> tuple[bytes, str, str]:
    headers = {
        "User-Agent": "Mozilla/5.0",  # минимально, без Accept и прочего
    }

    async with aiohttp.ClientSession(auto_decompress=False) as session:
        async with session.get(url, headers=headers, allow_redirects=False) as response:
            if response.status != 200:
                text = await response.text()
                raise Exception(
                    f"Не удалось скачать файл: {response.status}\n{text[:200]}"
                )

            file_bytes = await response.read()

            # Имя файла
            cd = response.headers.get("Content-Disposition")
            if cd and "filename=" in cd:
                filename = cd.split("filename=")[-1].strip('"; ')
            else:
                path = urlparse(url).path
                filename = os.path.basename(path)

            ext = os.path.splitext(filename)[-1].lower().lstrip(".")

            return file_bytes, filename, ext


async def load_input_file(data: GenerateSchema) -> tuple[bytes, str, str]:
    if data.url:
        logger.debug(f"Загрузка из URL: {data.url}")
        return await download_with_aiohttp_strict(data.url)

    elif data.file_name:
        filepath = TEMPLATES_DIR / data.file_name
        logger.debug(f"Загрузка локального файла: {filepath}")

        if not filepath.exists():
            logger.error(f"Файл не найден: {filepath}")
            raise FileNotFoundError(f"Файл не найден: {filepath}")

        filename = filepath.name
        with open(filepath, "rb") as f:
            file_bytes = f.read()

        logger.debug(
            f"Локальный файл прочитан: {filename}, размер: {len(file_bytes)} байт"
        )

    else:
        logger.error("Не указаны ни URL, ни имя файла")
        raise ValueError("Ни url, ни file_name не указаны")

    ext = os.path.splitext(filename)[-1].lower().lstrip(".")
    logger.debug(f"Расширение файла: {ext}")

    return file_bytes, filename, ext
