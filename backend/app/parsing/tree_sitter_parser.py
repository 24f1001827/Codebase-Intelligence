import tree_sitter_python as ts_python

from tree_sitter import Language, Parser

from app.models.code import CodeUnit
from app.parsing.parser import CodeParser


PYTHON_LANGUAGE = Language(ts_python.language())


class TreeSitterPythonParser(CodeParser):

    def __init__(self):
        self.parser = Parser(PYTHON_LANGUAGE)

    def parse(
        self,
        source: str,
        file_path: str,
        repository: str,
    ) -> list[CodeUnit]:

        source_bytes = source.encode("utf-8")

        tree = self.parser.parse(source_bytes)

        units = []

        self._extract_units(
            tree.root_node,
            source_bytes,
            file_path,
            repository,
            units,
        )

        return units
    
    def _extract_units(
        self,
        node,
        source_bytes: bytes,
        file_path: str,
        repository: str,
        units: list[CodeUnit],
        parent_name: str | None = None,
    ):
        if node.type in {"function_definition", "class_definition"}:

            name_node = node.child_by_field_name("name")

            if name_node is not None:
                name = source_bytes[
                    name_node.start_byte:name_node.end_byte
                ].decode("utf-8")

                if parent_name:
                    full_name = f"{parent_name}.{name}"
                else:
                    full_name = name

                unit_type = (
                    "class"
                    if node.type == "class_definition"
                    else "function"
                )

                content = source_bytes[
                    node.start_byte:node.end_byte
                ].decode("utf-8")

                units.append(
                    CodeUnit(
                        id=self._build_id(
                            repository,
                            file_path,
                            full_name,
                            node.start_point.row,
                            node.end_point.row,
                        ),
                        repository=repository,
                        file_path=file_path,
                        language="python",
                        unit_type=unit_type,
                        name=full_name,
                        start_line=node.start_point.row + 1,
                        end_line=node.end_point.row + 1,
                        content=content,
                    )
                )

                parent_name = full_name

        for child in node.children:
            self._extract_units(
                child,
                source_bytes,
                file_path,
                repository,
                units,
                parent_name,
            )

    @staticmethod
    def _build_id(
        repository: str,
        file_path: str,
        name: str,
        start_line: int,
        end_line: int,
    ) -> str:
        return (
            f"{repository}:"
            f"{file_path}:"
            f"{name}:"
            f"{start_line}:"
            f"{end_line}"
        )