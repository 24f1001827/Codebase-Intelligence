from app.parsing.tree_sitter_parser import TreeSitterPythonParser
from app.indexing.documents import code_units_to_documents
from app.indexing.vector_store import VectorStore


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


def main():
    parser = TreeSitterPythonParser()

    units = parser.parse(
        source=SOURCE,
        file_path="user_service.py",
        repository="test-repo",
    )

    documents = code_units_to_documents(units)

    vector_store = VectorStore()

    vector_store.add_documents(documents)

    results = vector_store.similarity_search(
        "Where does the application authenticate users?",
        k=3,
    )

    for result in results:
        print(
            result.metadata["name"],
            result.metadata["file_path"],
            result.metadata["start_line"],
            result.metadata["end_line"],
        )


if __name__ == "__main__":
    main()