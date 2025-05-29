from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, model_validator


class GenerateSchema(BaseModel):
    url: Optional[str] = Field(default=None)
    file_name: Optional[str] = Field(default=None)
    document_data: Dict[str, Any] = Field(
        ..., description="Данные, которые будут подставлены в шаблон"
    )
    name: str = Field(..., description="Название итогового файла без расширения")
    is_pdf: Optional[bool] = Field(
        default=False, description="Нужно ли сконвертировать результат в PDF"
    )

    @model_validator(mode="after")
    def validate_url_or_file_name(self) -> "GenerateSchema":
        if not self.url and not self.file_name:
            raise ValueError("Должно быть указано либо 'url', либо 'file_name'")
        return self
