from app.parsing.tree_sitter_parser import TreeSitterPythonParser


source = """
class UserService:

    def create_user(self, user):
        return save_user(user)

    def delete_user(self, user_id):
        return delete(user_id)


def authenticate(token):
    return verify(token)
"""


parser = TreeSitterPythonParser()

units = parser.parse(
    source=source,
    file_path="test.py",
    repository="test-repo",
)

for unit in units:
    print(
        unit.unit_type,
        unit.name,
        unit.start_line,
        unit.end_line,
    )