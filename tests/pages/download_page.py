from pathlib import Path
import time
from typing import Optional
import zipfile
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By

from .base_page import BasePage


class DownloadPage(BasePage):
    file_links_by = (By.CSS_SELECTOR, "#link-files ul li a")
    archive_link_by = (By.CSS_SELECTOR, "#link-archive a")

    def get_files_count(self) -> int:
        files = self.elements(self.file_links_by)
        return len(files)
    

    def get_files_names(self) -> list[str]:
        files = self.elements(self.file_links_by)
        return [file.text.strip() for file in files]


    def get_first_file_url(self) -> Optional[str]:
        files = self.elements(self.file_links_by)
        if files:
            return files[0].get_attribute("href")
        return None
    

    def get_archive_url(self) -> Optional[str]:
        element = self.element(self.archive_link_by)
        if element:
            return element.get_attribute("href")
        return None
