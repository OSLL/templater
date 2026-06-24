from typing import List, Tuple

TEMPLATE_DATA_COMBINATIONS = {
    '.docx': ['.xlsx', '.xls', '.csv'],
    '.odt': ['.xlsx', '.xls', '.csv'],
    '.ods': ['.xlsx', '.xls', '.csv'],
    '.pptx': ['.xlsx', '.xls', '.csv'],
    '.xlsx': ['.xlsx', '.xls', '.csv'],
}

TEST_FILES = {
    'templates': {
        '.docx': 'data/templates/template.docx',
        '.odt': 'data/templates/template.odt',
        '.ods': 'data/templates/template.ods',
        '.pptx': 'data/templates/template.pptx',
        '.xlsx': 'data/templates/template.xlsx',
    },
    'datatables': {
        '.xlsx': 'data/tables/datatable.xlsx',
        '.xls': 'data/tables/datatable.xls',
        '.csv': 'data/tables/datatable.csv',
    }
}

class CombinationGenerator:

    @staticmethod
    def get_all_combinations() -> List[Tuple[str, str]]:
        combinations = list()

        for template_ext, datatable_exts in TEMPLATE_DATA_COMBINATIONS.items():
            template_path = TEST_FILES["templates"].get(template_ext)

            if not template_path:
                continue

            for datatable_ext in datatable_exts:
                datatable_path = TEST_FILES['datatables'].get(datatable_ext)
                
                if not datatable_path:
                    continue
                
                combinations.append((
                    template_path,
                    datatable_path
                ))
        
        return combinations
    

    @staticmethod
    def get_combinations_by_template(template_ext: str) -> List[Tuple[str, str]]:
        combinations = list()

        if template_ext not in TEMPLATE_DATA_COMBINATIONS or TEST_FILES['templates'].get(template_ext) is None:
            return combinations
        
        template_path = TEST_FILES['templates'].get(template_ext)
        for datatable_ext in TEMPLATE_DATA_COMBINATIONS.get(template_ext):
            datatable_path = TEST_FILES['datatables'].get(datatable_ext)
            if datatable_path:
                combinations.append((
                    template_path,
                    datatable_path
                ))
        
        return combinations
    
    @staticmethod
    def get_combinations_by_datatable(datatable_ext: str) -> List[Tuple[str, str]]:
        combinations = list()

        for template_ext, datatable_exts in TEMPLATE_DATA_COMBINATIONS.items():
            if datatable_ext not in datatable_exts:
                continue

            template_path = TEST_FILES['templates'].get(template_ext)
            datatable_path = TEST_FILES['datatables'].get(datatable_ext)
            if template_path and datatable_path:
                combinations.append((
                    template_path,
                    datatable_path
                ))

        return combinations
    
