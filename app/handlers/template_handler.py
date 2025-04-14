from io import BytesIO
from jinja2 import Environment
from docxtpl import DocxTemplate
from openpyxl import load_workbook
from app.utils.context_builders import format_date, flatten_context


async def handle_docs(data: dict, template_bytes: bytes, extention: str):

    document_bytes = None

    if extention == "docx":
        document_bytes = generate_docx_from_bytes(template_bytes, data)
    elif extention == "xlsx":
        document_bytes = generate_excel_from_template(template_bytes, data)

    return document_bytes


def generate_docx_from_bytes(template_bytes: bytes, context: dict) -> bytes:
    doc_stream = BytesIO(template_bytes)
    doc = DocxTemplate(doc_stream)

    # Настроим Jinja-среду
    jinja_env = Environment()
    jinja_env.filters["format_date"] = format_date  # 👈 добавляем фильтр

    # Рендер с кастомной Jinja2-средой
    doc.render(context, jinja_env=jinja_env)

    output_stream = BytesIO()
    doc.save(output_stream)
    output_stream.seek(0)
    return output_stream.read()


def generate_excel_from_template(template_bytes: bytes, context: dict) -> bytes:
    flat_ctx = flatten_context(context)

    input_stream = BytesIO(template_bytes)
    workbook = load_workbook(input_stream)
    sheet = workbook.active

    for row in sheet.iter_rows():
        for cell in row:
            if isinstance(cell.value, str):
                for key, value in flat_ctx.items():
                    placeholder = f"{{{{ {key} }}}}"
                    if placeholder in cell.value:
                        cell.value = cell.value.replace(
                            placeholder, str(value))

    output_stream = BytesIO()
    workbook.save(output_stream)
    output_stream.seek(0)
    return output_stream.read()
