"""
Page Object for the Templater home page.

The page is a single-page wizard with four Bootstrap pill tabs:
  1. Upload Template  (#pills-template)
  2. Upload Data Table (#pills-datatable)
  3. Render           (#pills-render)
  4. Download         (#pills-result)

All upload interactions are AJAX-based; validation errors surface as browser
alert() dialogs, not inline DOM elements.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class HomePage:
    # ── selectors ──────────────────────────────────────────────────────────────

    # Template tab
    _TEMPLATE_INPUT      = (By.ID, "template-file")
    _UPLOAD_TEMPLATE_BTN = (By.ID, "btn-upload-template")
    _USE_TEMPLATE_BTN    = (By.ID, "btn-use-template")
    _TEMPLATE_NEXT_GROUP = (By.ID, "template-next-group")

    # Data-table tab
    _DATA_INPUT          = (By.ID, "data-table-file")
    _UPLOAD_DATA_BTN     = (By.ID, "btn-upload-data")
    _USE_DATA_BTN        = (By.ID, "btn-verify")
    _DATA_NEXT_GROUP     = (By.ID, "data-next-group")

    # Navigation
    _DATATABLE_TAB       = (By.ID, "pills-datatable-tab")

    def __init__(self, driver, base_url: str, default_timeout: int = 15):
        self.driver = driver
        self.base_url = base_url
        self._wait = WebDriverWait(driver, default_timeout)

    # ── navigation ─────────────────────────────────────────────────────────────

    def open(self) -> "HomePage":
        self.driver.get(self.base_url)
        self._wait.until(EC.presence_of_element_located(self._UPLOAD_TEMPLATE_BTN))
        return self

    def goto_data_tab(self) -> "HomePage":
        """
        Switch to the data-table tab.

        The tab is disabled by default until a template has been uploaded.
        We remove the Bootstrap 'disabled' class via JS so data-table upload
        tests can run independently without first uploading a template.
        """
        self.driver.execute_script(
            "$('#pills-datatable-tab').removeClass('disabled').tab('show');"
        )
        self._wait.until(EC.visibility_of_element_located(self._DATA_INPUT))
        return self

    # ── template tab ───────────────────────────────────────────────────────────

    def set_template_file(self, path: str) -> None:
        self.driver.find_element(*self._TEMPLATE_INPUT).send_keys(path)

    def click_upload_template(self) -> None:
        self.driver.find_element(*self._UPLOAD_TEMPLATE_BTN).click()

    def upload_template(self, path: str) -> None:
        self.set_template_file(path)
        self.click_upload_template()

    def wait_template_accepted(self, timeout: int = 20) -> None:
        """Block until the 'Use this template' button becomes clickable."""
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(self._USE_TEMPLATE_BTN)
        )

    def is_template_accepted(self) -> bool:
        """
        True if the template-next-group container is visible (d-none removed),
        which means the 'Use this template' button is shown after a successful upload.
        """
        el = self.driver.find_element(*self._TEMPLATE_NEXT_GROUP)
        return "d-none" not in (el.get_attribute("class") or "")

    # ── data-table tab ─────────────────────────────────────────────────────────

    def set_data_file(self, path: str) -> None:
        self.driver.find_element(*self._DATA_INPUT).send_keys(path)

    def click_upload_data(self) -> None:
        self.driver.find_element(*self._UPLOAD_DATA_BTN).click()

    def upload_data_table(self, path: str) -> None:
        self.set_data_file(path)
        self.click_upload_data()

    def wait_data_accepted(self, timeout: int = 20) -> None:
        """Block until the 'Use this data table' button becomes clickable."""
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(self._USE_DATA_BTN)
        )

    def is_data_accepted(self) -> bool:
        """
        True if the data-next-group container is visible (d-none removed),
        meaning the 'Use this data table' button appeared after a successful upload.
        """
        el = self.driver.find_element(*self._DATA_NEXT_GROUP)
        return "d-none" not in (el.get_attribute("class") or "")

    # ── alert helpers ──────────────────────────────────────────────────────────

    def get_alert_text_and_dismiss(self, timeout: int = 5) -> str:
        """Wait for a browser alert, capture its text, dismiss it, and return the text."""
        alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        text = alert.text
        alert.dismiss()
        return text
