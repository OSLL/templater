"""
Validation tests for the data-table upload step (tab 2).

The data-table tab is disabled until a template is uploaded.  The page fixture
below bypasses that guard via JavaScript so data-table tests can run in isolation.

Client-side checks (pure JS, no server needed):
  - No file selected            → alert "No file chosen"
  - Unsupported extension       → alert "File extension is not supported"
  - File exceeds 15 MB          → alert "File too large"

Server-round-trip checks (require running app + test reCAPTCHA keys):
  - Valid format                → 'Use this data table' button appears
  - Corrupted XLS               → server raises xlrd error → non-200 response
                                   → alert "Error occured when trying to upload..."
  - Corrupted CSV               → server fails on UTF-8 decode → same alert
  - Empty CSV                   → rejected server-side (HTTP 400) → error alert

Note on XLS/XLSX fixtures: generated with openpyxl (a transitive dep of docxtpl).
If openpyxl is not installed those parametrize branches are skipped automatically.
"""

import pytest
from selenium.common.exceptions import TimeoutException

from tests.pages.home_page import HomePage


@pytest.fixture
def page(driver, base_url):
    """Open the home page and force-navigate to the data-table tab."""
    return HomePage(driver, base_url).open().goto_data_tab()


@pytest.mark.parametrize("ext", ["csv", "xlsx", "xls"])
def test_valid_data_format_accepted(page, valid_data_tables, ext):
    """Uploading a data table in each supported format must succeed."""
    if ext not in valid_data_tables:
        pytest.skip(f"No fixture available for .{ext} – install openpyxl to enable")
    page.upload_data_table(valid_data_tables[ext])
    page.wait_data_accepted()
    assert page.is_data_accepted(), (
        f".{ext} data table should be accepted and the 'Use this data table' button should appear"
    )


@pytest.mark.parametrize("ext", ["txt", "pdf", "jpg"])
def test_invalid_data_format_rejected(page, generated_fixtures, ext):
    """Uploading a file with an unsupported extension must show an error alert."""
    page.upload_data_table(generated_fixtures[f"unsupported_{ext}"])
    alert_text = page.get_alert_text_and_dismiss()
    assert "not supported" in alert_text.lower(), (
        f"Expected 'not supported' in alert for .{ext}, got: {alert_text!r}"
    )
    assert not page.is_data_accepted(), (
        "Data acceptance button must not appear after an unsupported-format upload"
    )


def test_no_data_file_shows_error(page):
    """Clicking upload without selecting a file must show 'No file chosen'."""
    page.click_upload_data()
    alert_text = page.get_alert_text_and_dismiss()
    assert "no file" in alert_text.lower(), (
        f"Expected 'no file' alert, got: {alert_text!r}"
    )


def test_empty_data_file_rejected(page, generated_fixtures):
    """
    Uploading a 0-byte .csv file must be rejected.

    The server rejects empty uploads with HTTP 400 before storing them, so the
    JS shows an error alert and the acceptance button never appears.  We accept
    either outcome as evidence of proper rejection.
    """
    page.upload_data_table(generated_fixtures["empty_csv"])
    try:
        alert_text = page.get_alert_text_and_dismiss(timeout=5)
        assert alert_text, "Expected a non-empty error message for an empty data file"
    except TimeoutException:
        assert not page.is_data_accepted(), (
            "Empty data file must not result in the 'Use this data table' button appearing"
        )


def test_corrupted_xls_data_file_rejected(page, generated_fixtures):
    """
    Garbage bytes with a .xls extension: xlrd.open_workbook() raises, the server
    returns a non-200 response, and the JS shows an error alert.
    """
    page.upload_data_table(generated_fixtures["corrupted_xls"])
    alert_text = page.get_alert_text_and_dismiss(timeout=15)
    assert alert_text, "Expected an error alert for a corrupted .xls file"
    assert not page.is_data_accepted(), (
        "Data acceptance button must not appear after a corrupted XLS upload"
    )


def test_corrupted_csv_data_file_rejected(page, generated_fixtures):
    """
    Non-UTF-8 bytes with a .csv extension: the server-side decode() raises
    UnicodeDecodeError, producing a non-200 response and an error alert.
    """
    page.upload_data_table(generated_fixtures["corrupted_csv"])
    alert_text = page.get_alert_text_and_dismiss(timeout=15)
    assert alert_text, "Expected an error alert for a corrupted .csv file"
    assert not page.is_data_accepted(), (
        "Data acceptance button must not appear after a corrupted CSV upload"
    )


def test_large_data_file_rejected(page, generated_fixtures):
    """A .csv file larger than 15 MB must trigger the client-side 'File too large' alert."""
    page.upload_data_table(generated_fixtures["large_csv"])
    alert_text = page.get_alert_text_and_dismiss()
    assert "too large" in alert_text.lower(), (
        f"Expected 'too large' alert, got: {alert_text!r}"
    )
    assert not page.is_data_accepted()
