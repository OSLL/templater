from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage

class DatatablePage(BasePage):
    datatable_input_by = (By.CSS_SELECTOR, "#data-table-file")
    datatable_upload_btn_by = (By.CSS_SELECTOR, "#btn-upload-data")
    
    datatable_preview_by = (By.CSS_SELECTOR, "#div-data-table-preview table")

    datatable_submit_btn_by = (By.CSS_SELECTOR, "#btn-verify")
    datatable_reupload_btn_by = (By.CSS_SELECTOR, "#btn-upload-data")

    loading_modal_by = (By.ID, "loadingModal")

    render_tab_by = (By.ID, "pills-render")

    def upload_datatable(self, filepath):
        self.element(self.datatable_input_by).send_keys(filepath)

    def click_upload(self):
        self.click(self.datatable_upload_btn_by)

    def wait_preview(self):
        return self.wait.until(EC.visibility_of_element_located(self.datatable_preview_by))
    
    def click_use_datatable(self):
        self.click(self.datatable_submit_btn_by)    

    def wait_until_render_tab_active(self):
        self.wait.until(
            lambda x: "active" in x.find_element(*self.render_tab_by).get_attribute("class")
            and "show" in x.find_element(*self.render_tab_by).get_attribute("class")
        )