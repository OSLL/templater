from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage

class UploadPage(BasePage):
    template_input_by = (By.CSS_SELECTOR, "#template-file")
    template_upload_btn_by = (By.CSS_SELECTOR, "#btn-upload-template")
    
    tempate_preview_by = (By.CSS_SELECTOR, "#preview-container")
    
    template_submit_btn_by = (By.CSS_SELECTOR, "#btn-use-template")
    template_reupload_btn_by = (By.CSS_SELECTOR, "#btn-upload-template")

    datatable_tab_pill_by = (By.ID, "pills-datatable-tab")

    def upload_template(self, filepath):
        self.element(self.template_input_by).send_keys(filepath)

    def click_upload(self):
        self.click(self.template_upload_btn_by)

    def wait_preview(self):
        return self.wait.until(EC.visibility_of_element_located(self.tempate_preview_by))
    
    def click_use_template(self):
        self.click(self.template_submit_btn_by)

    def wait_until_datatable_pill_active(self):
        self.wait.until(
            EC.text_to_be_present_in_element_attribute(
                self.datatable_tab_pill_by,
                "aria-selected",
                "true"
            )
        )