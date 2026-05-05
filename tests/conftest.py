import pytest
from selenium import webdriver
from selenium.webdriver.remote.file_detector import LocalFileDetector
from pathlib import Path

from utils.combinations_generator import CombinationGenerator

GRID_URL = "http://selenium-hub:4444/wd/hub"
BASE_URL = "http://web:5000"

@pytest.fixture(scope="session")
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

@pytest.fixture(autouse=True)
def clean_between_tests(driver, base_url):
    driver.get(base_url)
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")
    
    yield
    
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")

@pytest.fixture
def base_url():
    return BASE_URL

def pytest_generate_tests(metafunc):
    if 'test_data_combination' in metafunc.fixturenames:
        combinations = CombinationGenerator.get_all_combinations()
        metafunc.parametrize(
            'test_data_combination',
            combinations,
            ids=[f"{Path(t).suffix[1:]}_{Path(d).suffix[1:]}" for t, d in combinations]
        )