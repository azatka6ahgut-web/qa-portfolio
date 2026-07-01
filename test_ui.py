import pytest
from pages.login_page import LoginPage
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from pages.checkbox_page import CheckboxPage
from pages.dropdown_page import DropdownPage

def test_checkbox_pom(browser):
    page = CheckboxPage(browser)
    page.open()
    
    # Проверяем начальное состояние
    assert not page.is_checked(0)  # первый не отмечен
    assert page.is_checked(1)      # второй отмечен
    
    # Кликаем первый
    page.click_checkbox(0)
    
    # Проверяем что изменилось
    assert page.is_checked(0)

@pytest.fixture
def browser():
    # Настройки браузера
    options = Options()
    options.add_argument("--headless")        # без окна
    options.add_argument("--no-sandbox")      # нужно для CI
    options.add_argument("--disable-dev-shm-usage")  # нужно для CI
    options.add_argument("--window-size=1920,1080")  # размер экрана
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options    # ← передаём настройки
    )
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

def test_google_title(browser):
    browser.get("https://google.com")
    assert "Google" in browser.title

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_google_search(browser):
    browser.get("https://google.com")
    search_box = browser.find_element(By.NAME, "q")
    search_box.send_keys("pytest tutorial")
    search_box.submit()
    
    # Ждём пока title изменится с "Google"
    WebDriverWait(browser, 10).until(
        lambda driver: "google" not in driver.title.lower() 
        or "pytest" in driver.title.lower()
    )
    
    assert "pytest" in browser.title.lower()


def test_login_success(browser):
    # ARRANGE
    page = LoginPage(browser)
    page.open()

    # ACT
    page.login("tomsmith", "SuperSecretPassword!")

    # ASSERT
    assert page.is_logged_in()

def test_login_wrong_password(browser):
    # ARRANGE
    page = LoginPage(browser)
    page.open()

    # ACT
    page.login("tomsmith", "wrongpassword")

    # ASSERT
    assert not page.is_logged_in()
    assert "invalid" in page.get_error_text()

def test_checkbox(browser):
     browser.get("https://the-internet.herokuapp.com/checkboxes")
     checkboxes = browser.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")

     checkbox1 = checkboxes[0]
     checkbox2 = checkboxes[1]

     assert not checkbox1.is_selected() 
     assert checkbox2.is_selected()

     checkbox1.click()

     assert checkbox1.is_selected()

def test_dropdown(browser):
    browser.get("https://the-internet.herokuapp.com/dropdown")
    dropdown = Select(browser.find_element(By.ID, "dropdown"))
    dropdown.select_by_visible_text("Option 1")
    assert dropdown.first_selected_option.text == "Option 1"
    dropdown.select_by_visible_text("Option 2")
    assert dropdown.first_selected_option.text == "Option 2"

def test_dynamic_loading(browser):
     browser.get("https://the-internet.herokuapp.com/dynamic_loading/1")
     browser.find_element(By.CSS_SELECTOR, "button").click()
     hello = WebDriverWait(browser, 10).until(
          EC.visibility_of_element_located((By.ID, "finish"))
     )
     assert "Hello World" in hello.text


def test_dropdown_pom(browser):
    page = DropdownPage(browser)
    page.open()
    
    page.select_option("Option 1")
    assert page.get_selected_text() == "Option 1"
    
    page.select_option("Option 2")
    assert page.get_selected_text() == "Option 2"