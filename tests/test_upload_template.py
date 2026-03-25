import os
from pages.upload_page import UploadPage
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def test_upload_template(driver, base_url):
    page = UploadPage(driver)

    template_path = os.path.abspath("data/templates/template.docx")
    print("PATH:", template_path)

    page.open(base_url)

    page.upload_template(template_path)

    page.click_upload()

    preview = page.wait_preview()
    assert preview is not None

    page.click_use_template()

    page.wait_until_datatable_pill_active()