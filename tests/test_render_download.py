"""
Validation tests for the render and download steps (tabs 3 and 4).

Rendering is the last stage that can reject a document: the template is
filled in once per data row and the results are offered for download.

  - Valid pair                 → one output file per data row, plus a zip
  - File-name pattern          → drives the names of the generated files
  - Download links             → resolve to a real, non-empty file
  - Corrupted template         → server responds status 'err'
                                 → alert "Something wrong occurred"
  - Start with another file    → wizard is reset back to tab 1

table.csv carries three data rows, so three output files are expected.
"""

import requests
import pytest

from tests.pages.home_page import HomePage


EXPECTED_OUTPUT_FILES = 3

RENDERABLE_FORMATS = ["docx", "odt", "xlsx"]


@pytest.fixture
def page(driver, base_url):
    return HomePage(driver, base_url).open()


def _run_full_flow(page, template_path, data_path):
    page.run_upload_steps(template_path, data_path)
    page.click_verify()
    page.wait_verification_done()
    page.click_generate()
    page.wait_render_done()
    return page


@pytest.mark.parametrize("ext", RENDERABLE_FORMATS)
def test_render_produces_one_file_per_data_row(page, valid_templates,
                                               valid_data_tables, ext):
    """Rendering must yield exactly one output document per row of the data table."""
    _run_full_flow(page, valid_templates[ext], valid_data_tables["csv"])

    files = page.generated_files()
    assert len(files) == EXPECTED_OUTPUT_FILES, (
        f".{ext}: expected {EXPECTED_OUTPUT_FILES} generated files, "
        f"got {len(files)}: {list(files)!r}"
    )
    assert all(name.endswith(f".{ext}") for name in files), (
        f".{ext}: generated files should keep the template extension, got {list(files)!r}"
    )


def test_render_offers_archive_of_all_files(page, valid_templates, valid_data_tables):
    """Alongside the individual files the result tab offers a zip of everything."""
    _run_full_flow(page, valid_templates["docx"], valid_data_tables["csv"])

    name, href = page.archive_link()
    assert name == "test.zip", f"Expected the archive to be named test.zip, got {name!r}"
    assert "file_id=" in href, f"Archive link has no file id: {href!r}"


@pytest.mark.parametrize("ext", RENDERABLE_FORMATS)
def test_generated_files_are_downloadable(page, valid_templates,
                                          valid_data_tables, ext):
    """Every download link must resolve to a real, non-empty document."""
    _run_full_flow(page, valid_templates[ext], valid_data_tables["csv"])

    files = page.generated_files()
    assert files, "No download links were rendered"

    for name, href in files.items():
        resp = requests.get(href, timeout=30)
        assert resp.status_code == 200, (
            f"{name}: download returned HTTP {resp.status_code}"
        )
        assert len(resp.content) > 0, f"{name}: downloaded file is empty"


def test_filename_pattern_drives_generated_names(page, valid_templates,
                                                 valid_data_tables):
    """The file-name pattern is rendered per row and becomes the output file name."""
    page.run_upload_steps(valid_templates["docx"], valid_data_tables["csv"])
    page.click_verify()
    page.wait_verification_done()

    page.set_filename_pattern("{{ last_name }}")
    page.click_generate()
    page.wait_render_done()

    assert sorted(page.generated_files()) == sorted(
        ["B.docx", "D.docx", "я.docx"]
    ), f"Unexpected generated file names: {sorted(page.generated_files())!r}"


def test_corrupted_template_never_reaches_render(page, generated_fixtures,
                                                 valid_data_tables):
    """
    A corrupted template must not be renderable at all.

    Verification fails and alerts, and because the render tab is unlocked only
    on a successful verification, the whole render stage stays out of reach
    and no files are ever produced.
    """
    page.run_upload_steps(generated_fixtures["corrupted_docx"],
                          valid_data_tables["csv"])
    page.click_verify()
    page.get_alert_text_and_dismiss(timeout=30)

    assert not page.is_render_tab_enabled(), (
        "The render tab must stay locked after a failed verification"
    )
    assert not page.is_result_tab_enabled(), (
        "The download tab must stay locked after a failed verification"
    )
    assert not page.generated_files(), (
        "A corrupted template must not produce download links"
    )


def test_start_over_resets_the_wizard(page, valid_templates, valid_data_tables):
    """'Start with another file' returns to tab 1 with the later tabs locked again."""
    _run_full_flow(page, valid_templates["docx"], valid_data_tables["csv"])

    page.click_start_over()

    assert page.is_template_accepted() is False, (
        "The template acceptance button should be hidden again after a reset"
    )
    assert page.is_data_accepted() is False, (
        "The data acceptance button should be hidden again after a reset"
    )
