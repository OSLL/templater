from pathlib import Path

from .base_parser import BaseParser
from .excel_parser import ExcelParser
from .csv_parser import CsvParser

from ..dataclasses.datatables import DataTable

PARSERS: list[BaseParser] = [
    ExcelParser(),
    CsvParser(),
]

def parse_table(file_path: str) -> DataTable:
    path = Path(file_path)
    for parser in PARSERS:
        if parser.supports(path):
            return parser.parse(path)
    
    raise ValueError(f"Unsupported file format: {path.suffix.lower()}")