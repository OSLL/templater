from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from pages import (
    TemplatePage,
    DatatablePage,
    RenderPage
)

def test_full_valid_template_flow(driver, base_url, test_data_combination):
    template_path, datatable_path = test_data_combination
    
    template_page = TemplatePage(driver)
    template_page.open(base_url)

    template_page.upload_template(template_path)
    template_page.click_upload()

    preview = template_page.wait_preview()
    assert preview is not None

    template_page.click_use_template()

    template_page.wait_until_datatable_tab_active()

    datatable_page = DatatablePage(driver)
    datatable_page.upload_datatable(datatable_path)
    datatable_page.click_upload()

    preview = datatable_page.wait_preview()
    assert preview is not None

    datatable_page.click_use_datatable()

    datatable_page.wait_until_render_tab_active()

    render_page = RenderPage(driver)
    assert render_page.is_filename_input_visible()
    
    columns = render_page.get_column_buttons_values()
    assert len(columns) == 3
