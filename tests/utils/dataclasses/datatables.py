from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class DataTable:
    headers: List[str]
    rows: List[List[str]]

    headers_count: int = field(init=False)
    rows_count: int = field(init=False)

    def __post_init__(self):
        self.headers_count = len(self.headers)
        self.rows_count = len(self.rows)