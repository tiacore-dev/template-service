from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class GenerateSchema(BaseModel):
    s3_key: str = Field(...,
                        description="Ключ шаблона в S3, например 'templates/contract.docx'")
    document_data: Dict[str, Any] = Field(
        ..., description="Данные, которые будут подставлены в шаблон")
    name: str = Field(...,
                      description="Название итогового файла без расширения")
    is_pdf: Optional[bool] = Field(
        False, description="Нужно ли сконвертировать результат в PDF")
