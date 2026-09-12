"""
Pytest configuration for Selenium-based UI validation tests.

Requirements:
  - Chrome + chromedriver installed and on PATH
  - App running at BASE_URL (default: http://localhost:5000)
    Use docker-compose.selenium.yml to start the whole stack (app + mongo +
    test runner); it sets RECAPTCHA_DISABLED=1 on the app, which is required
    for the tests that actually submit files to the server.
  - HEADLESS=0 env var to run Chrome visibly (useful for debugging)
  - BASE_URL env var to override the default server URL
    e.g. BASE_URL=http://web:5000 inside the Docker test container
"""

import os
import shutil

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

_HERE = os.path.dirname(os.path.abspath(__file__))
_APP_TEMPLATES = os.path.abspath(os.path.join(_HERE, "..", "app", "tests", "templates"))
_APP_DATA = os.path.abspath(os.path.join(_HERE, "..", "app", "tests", "data"))


@pytest.fixture(scope="session")
def base_url():
    return os.environ.get("BASE_URL", "http://localhost:5000")


@pytest.fixture
def driver():
    opts = Options()
    if os.environ.get("HEADLESS", "1") != "0":
        opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--window-size=1420,1080")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_bin = os.environ.get("CHROME_BIN")
    if chrome_bin:
        opts.binary_location = chrome_bin
    drv = webdriver.Chrome(options=opts)
    yield drv
    drv.quit()


@pytest.fixture(scope="session")
def valid_templates():
    """Absolute paths to valid template files (reused from app/tests/templates)."""
    return {
        ext: os.path.join(_APP_TEMPLATES, f"test.{ext}")
        for ext in ("docx", "xlsx", "pptx", "odt", "ods", "odp")
    }


@pytest.fixture(scope="session")
def valid_data_tables(tmp_path_factory):
    """
    Absolute paths to valid data-table files.
    CSV is reused from app/tests/data.
    XLSX and XLS are generated with openpyxl (a transitive dep of docxtpl).
    XLS is an XLSX file renamed – xlrd 1.2 auto-detects the format regardless
    of extension.
    """
    files = {"csv": os.path.join(_APP_DATA, "table.csv")}
    tmp = tmp_path_factory.mktemp("data_fixtures")
    try:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["name", "age"])
        ws.append(["Alice", 30])
        ws.append(["Bob", 25])
        xlsx = tmp / "data.xlsx"
        wb.save(str(xlsx))
        files["xlsx"] = str(xlsx)
        xls = tmp / "data.xls"
        shutil.copy(str(xlsx), str(xls))
        files["xls"] = str(xls)
    except ImportError:
        pass
    return files


@pytest.fixture(scope="session")
def generated_fixtures(tmp_path_factory):
    """
    Synthetic files for negative-path tests.
    Returns a dict: logical name -> absolute path string.

    Files generated:
      unsupported_<ext>   – plain bytes with an unsupported extension
      empty_docx          – 0-byte file with .docx extension
      empty_csv           – 0-byte file with .csv extension
      corrupted_docx      – garbage bytes with .docx extension
      corrupted_xls       – garbage bytes with .xls extension
      corrupted_csv       – non-UTF-8 bytes with .csv extension
      large_docx          – file just over the 15 MB client-side limit
      large_csv           – same, but .csv extension for data-table tests
    """
    tmp = tmp_path_factory.mktemp("fixtures")
    f = {}

    for ext in ("txt", "pdf", "jpg"):
        p = tmp / f"unsupported.{ext}"
        p.write_bytes(b"not a real document")
        f[f"unsupported_{ext}"] = str(p)

    for ext in ("docx", "csv"):
        p = tmp / f"empty.{ext}"
        p.write_bytes(b"")
        f[f"empty_{ext}"] = str(p)

    garbage = b"\x00\x01\x02\x03\xff\xfe\xfd" * 200
    for ext in ("docx", "xls"):
        p = tmp / f"corrupted.{ext}"
        p.write_bytes(garbage)
        f[f"corrupted_{ext}"] = str(p)

    p = tmp / "corrupted.csv"
    p.write_bytes(b"\xff\xfe" + garbage)
    f["corrupted_csv"] = str(p)

    over_limit = b"A" * (15 * 1024 * 1024 + 1)
    for ext in ("docx", "csv"):
        p = tmp / f"large.{ext}"
        p.write_bytes(over_limit)
        f[f"large_{ext}"] = str(p)

    return f
