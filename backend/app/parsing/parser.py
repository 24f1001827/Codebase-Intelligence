from abc import ABC, abstractmethod

from app.models.code import CodeUnit


class CodeParser(ABC):

    @abstractmethod
    def parse(
        self,
        source: str,
        file_path: str,
        repository: str,
    ) -> list[CodeUnit]:
        pass