from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import CodeUnitRecord, RepositoryRecord
from app.models.code import CodeUnit


class CodeUnitRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(
        self,
        code_unit: CodeUnit,
        repository_id: str,
    ) -> CodeUnitRecord:
        record = CodeUnitRecord(
            id=code_unit.id,
            repository_id=repository_id,
            file_path=code_unit.file_path,
            language=code_unit.language,
            unit_type=code_unit.unit_type,
            name=code_unit.name,
            start_line=code_unit.start_line,
            end_line=code_unit.end_line,
            content=code_unit.content,
        )

        self.session.add(record)
        return record

    def add_many(
        self,
        code_units: list[CodeUnit],
        repository_id: str,
    ) -> None:
        records = [
            CodeUnitRecord(
                id=unit.id,
                repository_id=repository_id,
                file_path=unit.file_path,
                language=unit.language,
                unit_type=unit.unit_type,
                name=unit.name,
                start_line=unit.start_line,
                end_line=unit.end_line,
                content=unit.content,
            )
            for unit in code_units
        ]

        self.session.add_all(records)

    def upsert_many(
        self,
        code_units: list[CodeUnit],
        repository_id: str,
    ) -> None:
        for unit in code_units:
            existing = self.get_by_id(unit.id)

            if existing is None:
                self.add(unit, repository_id)
                continue

            existing.repository_id = repository_id
            existing.file_path = unit.file_path
            existing.language = unit.language
            existing.unit_type = unit.unit_type
            existing.name = unit.name
            existing.start_line = unit.start_line
            existing.end_line = unit.end_line
            existing.content = unit.content

    def get_by_id(
        self,
        code_unit_id: str,
    ) -> CodeUnitRecord | None:
        statement = select(CodeUnitRecord).where(
            CodeUnitRecord.id == code_unit_id
        )

        return self.session.scalar(statement)

    def get_by_repository(
        self,
        repository_id: str,
    ) -> list[CodeUnitRecord]:
        statement = select(CodeUnitRecord).where(
            CodeUnitRecord.repository_id == repository_id
        )

        return list(self.session.scalars(statement).all())