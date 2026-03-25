import pytest
from selenium import webdriver
from selenium.webdriver.remote.file_detector import LocalFileDetector

GRID_URL = "http://selenium-hub:4444/wd/hub"
BASE_URL = "http://web:5000"

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.enable_downloads = True
    
    driver = webdriver.Remote(
        command_executor=GRID_URL,
        options=options
    )
    driver.file_detector = LocalFileDetector()

    yield driver

    driver.quit()

@pytest.fixture
def base_url():
    return BASE_URL