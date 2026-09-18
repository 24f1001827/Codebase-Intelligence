from pydantic import BaseModel, Field

class CodeUnit(BaseModel):
    id: str
    repository: str
    file_path: str
    language: str

    unit_type: str
    name: str

    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)

    content: str