from pathlib import Path
import csv

from .base_parser import BaseParser
from ..dataclasses.datatables import DataTable


class CsvParser(BaseParser):
    def supports(self, file_path: Path) -> bool:
        return file_path.suffix == ".csv"


    def parse(self, file_path: Path) -> DataTable:
        headers = []
        rows = []
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            
            for i, row in enumerate(reader):
                cleaned_row = [cell.strip() for cell in row]
                
                if i == 0:
                    headers = cleaned_row
                else:
                    rows.append(cleaned_row)
        
        return DataTable(
            headers=headers,
            rows=rows,
        )