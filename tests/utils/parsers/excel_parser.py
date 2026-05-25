from pathlib import Path
import xlrd
import openpyxl
from xlrd import sheet

from .base_parser import BaseParser
from ..dataclasses.datatables import DataTable


class ExcelParser(BaseParser):
    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in [".xlsx", ".xls"]


    def parse(self, file_path: Path) -> DataTable:
        match file_path.suffix:
            case ".xls":
                return self._parse_xls(file_path)
            case ".xlsx":
                return self._parse_xlsx(file_path)
            case _:
                return None
    

    def _parse_xls(self, file_path: Path) -> DataTable:
        wb = xlrd.open_workbook(file_path)
        sheet = wb.sheet_by_index(0)
        
        headers = list()
        rows = list()
        
        for row_idx in range(sheet.nrows):
            row = []
            for col_idx in range(sheet.ncols):
                cell = sheet.cell_value(row_idx, col_idx)
                if isinstance(cell, float):
                    cell = str(int(cell))
                data = cell.strip()
                
                if row_idx == 0:
                    headers.append(data)
                else:
                    row.append(data)
            
            if row_idx != 0:
                rows.append(row)

        return DataTable(
            headers=headers,
            rows=rows
        )   


    def _parse_xlsx(self, file_path: Path) -> DataTable:
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb.active

        headers = None
        rows = list()

        for i, row in enumerate(sheet.iter_rows(values_only=True)):
            values = list()
            for val in row:
                values.append(str(val).strip())
            
            if i == 0:
                headers = values
            else:
                rows.append(values)

        return DataTable(
            headers=headers,
            rows=rows
        )
        
