from langchain_core.documents import Document

from app.models.code import CodeUnit

def code_unit_to_document(code_unit: CodeUnit) -> Document:
    """
    Convert a CodeUnit to a Document.
    """
    return Document(
        page_content=code_unit.content,
        metadata = {
            "id": code_unit.id,
            "repository": code_unit.repository,
            "file_path": code_unit.file_path,
            "language": code_unit.language,
            "unit_type": code_unit.unit_type,
            "name": code_unit.name,
            "start_line": code_unit.start_line,
            "end_line": code_unit.end_line,
            },
        )

def code_units_to_documents(code_units: list[CodeUnit]) -> list[Document]:
    """
    Convert a list of CodeUnits to a list of Documents.
    """
    return [code_unit_to_document(code_unit) for code_unit in code_units]