import array

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage

class RenderPage(BasePage):
    filename_input_by = (By.CSS_SELECTOR, "#filename-template")
    generate_btn_by = (By.CSS_SELECTOR, "#btn-generate")
    
    column_buttons_by = (By.CSS_SELECTOR, "#field-list > input[type='button']")

    result_tab_by = (By.ID, "pills-result")

    def is_filename_input_visible(self):
        return self.element(self.filename_input_by).is_displayed()
    
    def set_filename_value(self, value: str):
        self.element(self.filename_input_by).clear()
        self.type(self.filename_input_by, value)

    def get_column_buttons_values(self) -> list[str]:
        values = list()
        for elem in self.elements(self.column_buttons_by):
            values.append(elem.get_attribute("value"))
        return values
    
    def wait_until_result_tab_active(self):
        self.wait.until(
            lambda x: "active" in x.find_element(*self.result_tab_by).get_attribute("class")
            and "show" in x.find_element(*self.result_tab_by).get_attribute("class")
        )
    
