from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.models.code import CodeUnit


class Base(DeclarativeBase):
    pass


class RepositoryRecord(Base):
    __tablename__ = "repositories"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    name: Mapped[str] = mapped_column(String, index=True)

    source_type: Mapped[str] = mapped_column(String, index=True)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)

    local_path: Mapped[str] = mapped_column(String)

    current_commit: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    code_units: Mapped[list["CodeUnitRecord"]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
    )


class CodeUnitRecord(Base):
    __tablename__ = "code_units"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    repository_id: Mapped[str] = mapped_column(
        ForeignKey("repositories.id"),
        index=True,
    )

    file_path: Mapped[str] = mapped_column(String, index=True)
    language: Mapped[str] = mapped_column(String, index=True)
    unit_type: Mapped[str] = mapped_column(String, index=True)
    name: Mapped[str] = mapped_column(String, index=True)

    start_line: Mapped[int] = mapped_column(Integer)
    end_line: Mapped[int] = mapped_column(Integer)

    content: Mapped[str] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    repository: Mapped["RepositoryRecord"] = relationship(
        back_populates="code_units",
    )

    def to_code_unit(self) -> CodeUnit:
        return CodeUnit(
            id=self.id,
            repository=self.repository_id,
            file_path=self.file_path,
            language=self.language,
            unit_type=self.unit_type,
            name=self.name,
            start_line=self.start_line,
            end_line=self.end_line,
            content=self.content,
        )