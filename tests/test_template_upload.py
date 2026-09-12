"""
Validation tests for the template upload step (tab 1).

Client-side checks (pure JS, no server needed):
  - No file selected            → alert "No file chosen"
  - Unsupported extension       → alert "File extension is not supported"
  - File exceeds 15 MB          → alert "File too large"

Server-round-trip checks (require running app + test reCAPTCHA keys):
  - Valid format                → 'Use this template' button appears
  - Empty file                  → rejected server-side (HTTP 400) → error alert
  - Corrupted file (garbage)    → upload is accepted by the server (no content
                                   inspection at upload time); error surfaces only
                                   at verify/render time
"""

import pytest
from selenium.common.exceptions import TimeoutException

from tests.pages.home_page import HomePage


@pytest.fixture
def page(driver, base_url):
    return HomePage(driver, base_url).open()


@pytest.mark.parametrize("ext", ["docx", "xlsx", "pptx", "odt", "ods", "odp"])
def test_valid_template_format_accepted(page, valid_templates, ext):
    """Uploading a template in each supported format must succeed."""
    page.upload_template(valid_templates[ext])
    page.wait_template_accepted()
    assert page.is_template_accepted(), (
        f".{ext} template should be accepted and the 'Use this template' button should appear"
    )


@pytest.mark.parametrize("ext", ["txt", "pdf", "jpg"])
def test_invalid_template_format_rejected(page, generated_fixtures, ext):
    """Uploading a file with an unsupported extension must show an error alert."""
    page.upload_template(generated_fixtures[f"unsupported_{ext}"])
    alert_text = page.get_alert_text_and_dismiss()
    assert "not supported" in alert_text.lower(), (
        f"Expected 'not supported' in alert for .{ext}, got: {alert_text!r}"
    )
    assert not page.is_template_accepted(), (
        "Template acceptance button must not appear after an unsupported-format upload"
    )


def test_no_template_file_shows_error(page):
    """Clicking upload without selecting a file must show 'No file chosen'."""
    page.click_upload_template()
    alert_text = page.get_alert_text_and_dismiss()
    assert "no file" in alert_text.lower(), (
        f"Expected 'no file' alert, got: {alert_text!r}"
    )


def test_empty_template_rejected(page, generated_fixtures):
    """
    Uploading a 0-byte file with a .docx extension must be rejected.

    The server rejects empty uploads with HTTP 400 before storing them in
    GridFS, so the JS shows an error alert and the acceptance button stays
    hidden.  Either outcome is accepted as evidence of rejection.
    """
    page.upload_template(generated_fixtures["empty_docx"])
    try:
        alert_text = page.get_alert_text_and_dismiss(timeout=5)
        assert alert_text, "Expected a non-empty error message for an empty template"
    except TimeoutException:
        assert not page.is_template_accepted(), (
            "Empty template must not be accepted (no 'Use this template' button)"
        )


def test_corrupted_template_handled_gracefully(page, generated_fixtures):
    """
    Uploading garbage bytes with a .docx extension must not crash the UI.

    The server stores template files without content validation; errors only
    surface during verify/render.  We assert that the upload step completes
    without an unhandled JS error and that the UI remains functional (the
    'Use this template' button appears as it does for any stored file).
    """
    page.upload_template(generated_fixtures["corrupted_docx"])
    page.wait_template_accepted()
    assert page.is_template_accepted(), (
        "Corrupted template: upload should complete without a UI crash "
        "(content errors surface later at verify/render)"
    )


def test_large_template_rejected(page, generated_fixtures):
    """A file larger than 15 MB must trigger the client-side 'File too large' alert."""
    page.upload_template(generated_fixtures["large_docx"])
    alert_text = page.get_alert_text_and_dismiss()
    assert "too large" in alert_text.lower(), (
        f"Expected 'too large' alert, got: {alert_text!r}"
    )
    assert not page.is_template_accepted()
