from abc import ABC, abstractmethod
from pathlib import Path

from ..dataclasses.datatables import DataTable


class BaseParser(ABC):
    @abstractmethod
    def supports(self, file_path: Path) -> bool:
        pass
    

    @abstractmethod
    def parse(self, file_path: Path) -> DataTable:
        pass