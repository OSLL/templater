"""
Page Object for the Templater home page.

The page is a single-page wizard with four Bootstrap pill tabs:
  1. Upload Template   (#pills-template)
  2. Upload Data Table (#pills-datatable)
  3. Render            (#pills-render)
  4. Download          (#pills-result)

All upload interactions are AJAX-based; validation errors surface as browser
alert() dialogs, not inline DOM elements.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class HomePage:

    _TEMPLATE_INPUT      = (By.ID, "template-file")
    _UPLOAD_TEMPLATE_BTN = (By.ID, "btn-upload-template")
    _USE_TEMPLATE_BTN    = (By.ID, "btn-use-template")
    _TEMPLATE_NEXT_GROUP = (By.ID, "template-next-group")

    _DATA_INPUT      = (By.ID, "data-table-file")
    _UPLOAD_DATA_BTN = (By.ID, "btn-upload-data")
    _USE_DATA_BTN    = (By.ID, "btn-verify")
    _DATA_NEXT_GROUP = (By.ID, "data-next-group")

    _VERIFICATION_RESULT = (By.ID, "verificationResult")
    _FILENAME_TEMPLATE   = (By.ID, "filename-template")
    _FIELD_LIST          = (By.ID, "field-list")
    _FIELD_BUTTONS       = (By.CSS_SELECTOR, "#field-list input")
    _GENERATE_BTN        = (By.ID, "btn-generate")

    _FILE_LINKS     = (By.CSS_SELECTOR, "#link-files ul li a")
    _ARCHIVE_LINK   = (By.CSS_SELECTOR, "#link-archive a")
    _START_OVER_BTN = (By.CSS_SELECTOR, "#pills-result .text-center input")

    _LOADING_MODAL = (By.ID, "loadingModal")
    _DATATABLE_TAB = (By.ID, "pills-datatable-tab")
    _RENDER_TAB    = (By.ID, "pills-render-tab")
    _RESULT_TAB    = (By.ID, "pills-result-tab")

    def __init__(self, driver, base_url: str, default_timeout: int = 15):
        self.driver = driver
        self.base_url = base_url
        self._wait = WebDriverWait(driver, default_timeout)

    def open(self, locale: str = "en") -> "HomePage":
        self.driver.get(self.base_url)
        self.driver.add_cookie({"name": "_LOCALE_", "value": locale})
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

    def click_use_template(self) -> None:
        self.driver.find_element(*self._USE_TEMPLATE_BTN).click()
        self._wait.until(EC.visibility_of_element_located(self._DATA_INPUT))

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

    def click_verify(self) -> None:
        self.driver.find_element(*self._USE_DATA_BTN).click()

    def _wait_modal_dismissed(self, timeout: int = 30) -> None:
        """
        Block until the loading modal and its backdrop are really gone.

        The page hides the modal half a second after the response arrives, so
        an element can be reported clickable while the backdrop still covers
        it and swallows the interaction.
        """
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script(
                "return document.querySelectorAll('.modal-backdrop').length === 0"
                " && !$('#loadingModal').hasClass('show');"
            )
        )

    def wait_verification_done(self, timeout: int = 30) -> None:
        """Block until /verify answered and the render stage is interactable."""
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(self._GENERATE_BTN)
        )
        self._wait_modal_dismissed(timeout)
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self._FILENAME_TEMPLATE)
        )

    def run_upload_steps(self, template_path: str, data_path: str) -> "HomePage":
        """Walk stages 1-2: upload a template and a data table, then move on."""
        self.upload_template(template_path)
        self.wait_template_accepted()
        self.click_use_template()
        self.upload_data_table(data_path)
        self.wait_data_accepted()
        return self

    def verification_html(self) -> str:
        return self.driver.find_element(
            *self._VERIFICATION_RESULT).get_attribute("innerHTML")

    def verification_messages(self) -> list:
        el = self.driver.find_element(*self._VERIFICATION_RESULT)
        return [p.text for p in el.find_elements(By.TAG_NAME, "p")]

    def field_names(self) -> list:
        return [
            b.get_attribute("value")
            for b in self.driver.find_elements(*self._FIELD_BUTTONS)
        ]

    def get_filename_pattern(self) -> str:
        return self.driver.find_element(
            *self._FILENAME_TEMPLATE).get_attribute("value")

    def set_filename_pattern(self, pattern: str) -> None:
        el = self.driver.find_element(*self._FILENAME_TEMPLATE)
        el.clear()
        el.send_keys(pattern)

    def click_field_button(self, name: str) -> None:
        for b in self.driver.find_elements(*self._FIELD_BUTTONS):
            if b.get_attribute("value") == name:
                b.click()
                return
        raise AssertionError("No field button named {!r}".format(name))

    def is_render_tab_enabled(self) -> bool:
        el = self.driver.find_element(*self._RENDER_TAB)
        return "disabled" not in (el.get_attribute("class") or "")

    def is_result_tab_enabled(self) -> bool:
        el = self.driver.find_element(*self._RESULT_TAB)
        return "disabled" not in (el.get_attribute("class") or "")

    def click_generate(self) -> None:
        self.driver.find_element(*self._GENERATE_BTN).click()

    def wait_render_done(self, timeout: int = 40) -> None:
        """Block until /render answered and the download links were rendered."""
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(self._START_OVER_BTN)
        )
        self._wait_modal_dismissed(timeout)

    def generated_files(self) -> dict:
        """Map of generated file name -> download href, from the Download tab."""
        return {
            a.text: a.get_attribute("href")
            for a in self.driver.find_elements(*self._FILE_LINKS)
        }

    def archive_link(self) -> tuple:
        el = self.driver.find_element(*self._ARCHIVE_LINK)
        return el.text, el.get_attribute("href")

    def click_start_over(self) -> None:
        self.driver.find_element(*self._START_OVER_BTN).click()

    def get_alert_text_and_dismiss(self, timeout: int = 5) -> str:
        """Wait for a browser alert, capture its text, dismiss it, and return the text."""
        alert = WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        text = alert.text
        alert.dismiss()
        return text
