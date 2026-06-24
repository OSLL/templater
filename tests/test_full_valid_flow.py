from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from pages import (
    TemplatePage,
    DatatablePage,
    RenderPage,
    DownloadPage
)
from utils.parsers import parse_table
from utils.helpers_funcs import (
    normalize_filename,
    download_file,
    download_archive_and_unzip
)


def test_full_valid_template_flow(driver, base_url, test_data_combination, download_dir):
    template_path, datatable_path = test_data_combination
    datatable = parse_table(datatable_path)
    
    template_page = TemplatePage(driver)
    template_page.open(base_url)

    template_page.upload_template(template_path)
    template_page.click_upload()

    preview = template_page.wait_preview()
    assert preview is not None, "template preview doesn't shown"

    template_page.click_use_template()

    template_page.wait_until_datatable_tab_active()

    datatable_page = DatatablePage(driver)
    datatable_page.upload_datatable(datatable_path)
    datatable_page.click_upload()

    preview = datatable_page.wait_preview()
    assert preview is not None, "datatable preview doesn't shown"

    datatable_page.click_use_datatable()

    datatable_page.wait_until_render_tab_active()

    render_page = RenderPage(driver)
    assert render_page.is_filename_input_visible(), "filename input not visible"
    
    columns = render_page.get_column_buttons_values()
    assert len(columns) == datatable.headers_count, f"columns count {len(columns)} != headers count {datatable.headers_count}"
    for i, col in enumerate(columns):
        assert col == datatable.headers[i], "column button contains wrong header"

    filename_template = "{{ " + " }}_{{ ".join(datatable.headers) + " }}"
    render_page.set_filename_value(filename_template)

    render_page.click_generate()
    render_page.wait_until_result_tab_active()

    download_page = DownloadPage(driver)

    assert download_page.get_files_count() == datatable.rows_count, \
        "file links count != datatable rows"
    for i, filename in enumerate(download_page.get_files_names()):
        expected_filename = "_".join(datatable.rows[i])
        normalized_filename = normalize_filename(filename)
        assert expected_filename == normalized_filename, \
            f"Expected filename: {expected_filename}, got: {normalized_filename}"

    first_url = download_page.get_first_file_url()
    ok, _ = download_file(first_url, download_dir)
    assert ok, "first file download failed"

    archive_url = download_page.get_archive_url()
    ok, files = download_archive_and_unzip(archive_url, download_dir)
    assert ok, "cannot download archive files"
    assert len(files) == datatable.rows_count, \
        f"archive contains less files: expected={datatable.rows_count} got={len(files)}"

    expected_filenames = ["_".join(row) for row in datatable.rows]
    for file in files:
        assert normalize_filename(file.name) in expected_filenames, \
            f"archive contains unexpected file: {file.name}"
