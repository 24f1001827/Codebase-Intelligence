from pathlib import Path

from app.ingestion.repository import discover_files
from app.parsing.language import detect_language
from app.parsing.tree_sitter_parser import TreeSitterPythonParser

from app.indexing.documents import code_units_to_documents
from app.indexing.vector_store import VectorStore

from app.database.connection import SessionLocal
from app.database.repository_repository import RepositoryRepository
from app.database.code_unit_repository import CodeUnitRepository


class Indexer:
    def __init__(self):
        self.vector_store = VectorStore()

        self.parsers = {
            "python": TreeSitterPythonParser(),
        }

    def index_repository(self, repo_path: str) -> int:
        root = Path(repo_path).resolve()
        files = discover_files(str(root))

        with SessionLocal() as session:
            repository_repository = RepositoryRepository(session)
            repository = repository_repository.get_or_create_local(
                str(root)
            )

            code_unit_repository = CodeUnitRepository(session)

            total_units = 0

            # ---------------------------------------------------------
            # Remove code units belonging to files that no longer exist
            # ---------------------------------------------------------

            discovered_file_paths = {
                str(file_path.relative_to(root))
                for file_path in files
            }

            existing_repository_units = (
                code_unit_repository.get_by_repository(
                    repository.id
                )
            )

            stale_file_ids = [
                unit.id
                for unit in existing_repository_units
                if unit.file_path not in discovered_file_paths
            ]

            code_unit_repository.delete_many(stale_file_ids)

            self.vector_store.delete_documents(
                stale_file_ids
            )

            # ---------------------------------------------------------
            # Process discovered files
            # ---------------------------------------------------------

            for file_path in files:
                language = detect_language(str(file_path))

                if language is None:
                    continue

                parser = self.parsers.get(language)

                if parser is None:
                    continue

                source = file_path.read_text(
                    encoding="utf-8"
                )

                relative_path = str(
                    file_path.relative_to(root)
                )

                units = parser.parse(
                    source=source,
                    file_path=relative_path,
                    repository=repository.id,
                )

                # -----------------------------------------------------
                # Remove stale code units from files that still exist
                # -----------------------------------------------------

                existing_units = (
                    code_unit_repository.get_by_file(
                        repository_id=repository.id,
                        file_path=relative_path,
                    )
                )

                existing_ids = {
                    unit.id
                    for unit in existing_units
                }

                new_ids = {
                    unit.id
                    for unit in units
                }

                stale_ids = existing_ids - new_ids

                code_unit_repository.delete_many(
                    list(stale_ids)
                )

                self.vector_store.delete_documents(
                    list(stale_ids)
                )

                # -----------------------------------------------------
                # Add/update current code units
                # -----------------------------------------------------

                if units:
                    code_unit_repository.upsert_many(
                        units,
                        repository_id=repository.id,
                    )

                    documents = code_units_to_documents(
                        units
                    )

                    self.vector_store.add_documents(
                        documents
                    )

                total_units += len(units)

            session.commit()

        return total_units