from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import RepositoryRecord


class RepositoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(
        self,
        repository_id: str,
    ) -> RepositoryRecord | None:
        statement = select(RepositoryRecord).where(
            RepositoryRecord.id == repository_id
        )

        return self.session.scalar(statement)

    def get_by_local_path(
        self,
        local_path: str,
    ) -> RepositoryRecord | None:
        normalized_path = local_path.replace("\\", "/").rstrip("/")

        statement = select(RepositoryRecord).where(
            RepositoryRecord.local_path == normalized_path
        )

        return self.session.scalar(statement)

    def create(
        self,
        name: str,
        source_type: str,
        local_path: str,
        source_url: str | None = None,
        current_commit: str | None = None,
    ) -> RepositoryRecord:
        repository = RepositoryRecord(
            id=f"repo_{uuid4().hex}",
            name=name,
            source_type=source_type,
            source_url=source_url,
            local_path=local_path.replace("\\", "/").rstrip("/"),
            current_commit=current_commit,
        )

        self.session.add(repository)

        return repository

    def get_or_create_local(
        self,
        local_path: str,
    ) -> RepositoryRecord:
        normalized_path = local_path.replace("\\", "/").rstrip("/")

        existing = self.get_by_local_path(normalized_path)

        if existing is not None:
            return existing

        name = normalized_path.split("/")[-1]

        return self.create(
            name=name,
            source_type="local",
            local_path=normalized_path,
        )