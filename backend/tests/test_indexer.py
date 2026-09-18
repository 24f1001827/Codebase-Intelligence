from pathlib import Path
from tempfile import TemporaryDirectory

from sqlalchemy import select

from app.indexing.indexer import Indexer
from app.database.connection import SessionLocal
from app.database.models import CodeUnitRecord, RepositoryRecord


SOURCE = """
class UserService:

    def create_user(self, user):
        validate_user(user)
        return save_user(user)

    def delete_user(self, user_id):
        return delete_from_database(user_id)


def authenticate(username, password):
    return check_credentials(username, password)
"""


with TemporaryDirectory() as temp_dir:
    root = Path(temp_dir)

    source_file = root / "user_service.py"
    source_file.write_text(SOURCE, encoding="utf-8")

    indexer = Indexer()

    print("First indexing:")
    total_units = indexer.index_repository(str(root))
    print("Units indexed:", total_units)

    print("\nSecond indexing:")
    total_units = indexer.index_repository(str(root))
    print("Units indexed:", total_units)

    collection = indexer.vector_store.client.get_collection(
        collection_name=indexer.vector_store.collection_name
    )

    print("\nQDRANT:")
    print("Point count:", collection.points_count)

    points, _ = indexer.vector_store.client.scroll(
        collection_name=indexer.vector_store.collection_name,
        limit=20,
        with_payload=True,
        with_vectors=False,
    )

    print("\nQDRANT POINTS:")

    for point in points:
        print(
            "ID:",
            point.id,
            "| CodeUnit ID:",
            point.payload.get("metadata", {}).get("id"),
        )

    with SessionLocal() as session:
        normalized_root = (
            str(root.resolve())
            .replace("\\", "/")
            .rstrip("/")
        )
        repository_id = f"local:{normalized_root}"

        print("\nTEST ROOT:")
        print("Raw:", repr(str(root)))
        print("Normalized:", repr(normalized_root))

        repository_statement = select(RepositoryRecord).where(
            RepositoryRecord.local_path == normalized_root
        )

        repository = session.scalar(repository_statement)

        print("\nREPOSITORY:")

        if repository is None:
            print("Repository was NOT found.")
        else:
            print("ID:", repository.id)
            print("Name:", repository.name)
            print("Source type:", repository.source_type)
            print("Local path:", repository.local_path)

            code_unit_statement = select(CodeUnitRecord).where(
                CodeUnitRecord.repository_id == repository.id
            )

            records = session.scalars(code_unit_statement).all()

            points, _ = indexer.vector_store.client.scroll(
                collection_name=indexer.vector_store.collection_name,
                limit=100,
                with_payload=True,
                with_vectors=False,
            )

            repository_points = [
                point
                for point in points
                if point.payload.get("metadata", {})
                .get("id", "")
                .startswith(repository.id + ":")
            ]

            print("\nCODE UNITS:")

            for record in records:
                print(
                    record.name,
                    "| repository_id:",
                    record.repository_id,
                )

            print("\nTESTS:")

            print(
                "Repository exists:",
                repository is not None,
            )

            print(
                "Correct source type:",
                repository.source_type == "local",
            )

            print(
                "Correct local path:",
                repository.local_path == normalized_root,
            )

            print(
                "All units linked to repository:",
                all(
                    record.repository_id == repository.id
                    for record in records
                ),
            )

            print(
                "Correct number of units:",
                len(records) == 4,
            )

            print(
                "Correct Qdrant point count:",
                len(repository_points) == 4,
            )