from app.database.connection import SessionLocal
from backend.app.database.code_unit_repository import CodeUnitRepository
from app.models.code import CodeUnit


code_unit = CodeUnit(
    id="test:user_service.py:authenticate:1:3",
    repository="test-repository",
    file_path="user_service.py",
    language="python",
    unit_type="function",
    name="authenticate",
    start_line=1,
    end_line=3,
    content=(
        "def authenticate(username, password):\n"
        "    return check_credentials(username, password)"
    ),
)


with SessionLocal() as session:
    repository = CodeUnitRepository(session)

    existing = repository.get_by_id(code_unit.id)

    if existing is None:
        repository.add(code_unit)
        session.commit()
        saved = repository.get_by_id(code_unit.id)
    else:
        saved = existing

    print(saved.name)
    print(saved.file_path)
    print(saved.start_line)
    print(saved.end_line)
    print(saved.content)