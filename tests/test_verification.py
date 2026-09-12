"""
Validation tests for the verification step (tab 3).

Verification is where the uploaded documents are parsed for the first time:
the renderer extracts the jinja2 placeholders from the template and compares
them against the columns of the data table.

  - Valid template + table     → per-format field-mismatch report
  - Fully matching pair        → "Verification done without warning"
  - Corrupted template         → server raises, responds status 'err'
                                 → alert "Something wrong occurred"
  - Successful verification    → field buttons and a default file-name
                                 pattern are offered for the render step

Expected messages are asserted in English, so the page object sets the
_LOCALE_ cookie to "en" before the /verify round trip.
"""

import pytest

from tests.pages.home_page import HomePage


VERIFICATION_EXPECTATIONS = [
    ("odt",  ["'age' not defined in the template", "'address' not defined in the csv"]),
    ("docx", ["Verification done without warning"]),
    ("odp",  ["'asd' not defined in the csv"]),
    ("pptx", ["'asd' not defined in the csv"]),
    ("ods",  ["'age' not defined in the template"]),
    ("xlsx", ["'age' not defined in the template"]),
]


@pytest.fixture
def page(driver, base_url):
    return HomePage(driver, base_url).open()


@pytest.mark.parametrize("ext,expected", VERIFICATION_EXPECTATIONS,
                         ids=[e for e, _ in VERIFICATION_EXPECTATIONS])
def test_verification_reports_field_mismatches(page, valid_templates,
                                               valid_data_tables, ext, expected):
    """Each template format must be verified against the CSV with the documented result."""
    page.run_upload_steps(valid_templates[ext], valid_data_tables["csv"])
    page.click_verify()
    page.wait_verification_done()

    assert page.verification_messages() == expected, (
        f"Unexpected verification report for .{ext}: "
        f"{page.verification_messages()!r}"
    )


def test_verification_offers_csv_fields_for_naming(page, valid_templates,
                                                   valid_data_tables):
    """After verification the CSV columns are offered as file-name building blocks."""
    page.run_upload_steps(valid_templates["docx"], valid_data_tables["csv"])
    page.click_verify()
    page.wait_verification_done()

    assert page.field_names() == ["first_name", "last_name", "age"], (
        f"Expected the CSV columns as field buttons, got {page.field_names()!r}"
    )
    assert page.get_filename_pattern() == "{{ first_name }}", (
        "The first CSV column should seed the default file-name pattern, "
        f"got {page.get_filename_pattern()!r}"
    )


def test_field_button_appends_to_filename_pattern(page, valid_templates,
                                                  valid_data_tables):
    """Clicking a field button appends that field as a jinja2 tag to the pattern."""
    page.run_upload_steps(valid_templates["docx"], valid_data_tables["csv"])
    page.click_verify()
    page.wait_verification_done()

    page.set_filename_pattern("")
    page.click_field_button("last_name")

    assert page.get_filename_pattern() == "{{ last_name }}", (
        f"Expected '{{{{ last_name }}}}', got {page.get_filename_pattern()!r}"
    )


def test_verification_of_corrupted_template_rejected(page, generated_fixtures,
                                                     valid_data_tables):
    """
    A template that passed upload but is not a real document must fail here.

    Upload stores the bytes without inspecting them, so garbage with a .docx
    extension only blows up once the renderer opens it; verify_doc catches
    that and answers status 'err', which the JS surfaces as an alert.
    """
    page.run_upload_steps(generated_fixtures["corrupted_docx"],
                          valid_data_tables["csv"])
    page.click_verify()

    alert_text = page.get_alert_text_and_dismiss(timeout=30)
    assert "something wrong" in alert_text.lower(), (
        f"Expected a verification error alert, got: {alert_text!r}"
    )
