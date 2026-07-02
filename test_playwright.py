import pytest
from playwright.sync_api import sync_playwright, Page


@pytest.fixture
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()


def test_google_title(page):
    page.goto("https://google.com")
    assert "Google" in page.title()


def test_login_success(page):
    page.goto("https://the-internet.herokuapp.com/login")
    page.fill("#username", "tomsmith")
    page.fill("#password", "SuperSecretPassword!")
    page.click("button[type='submit']")
    assert "secure" in page.url

def test_login_wrong_password(page):
    page.goto("https://the-internet.herokuapp.com/login")
    page.fill("#username", "tomsmith")
    page.fill("#password", "wrongpassword")
    page.click("button[type='submit']")
    
    assert "login" in page.url
    error = page.locator("#flash")
    assert "invalid" in error.inner_text().lower()


def test_checkboxes(page):
    page.goto("https://the-internet.herokuapp.com/checkboxes")
    
    checkboxes = page.locator("input[type='checkbox']")
    
    assert not checkboxes.nth(0).is_checked()  # первый не отмечен
    assert checkboxes.nth(1).is_checked()       # второй отмечен
    
    checkboxes.nth(0).click()
    assert checkboxes.nth(0).is_checked()       # теперь отмечен!


def test_dropdown(page):
    page.goto("https://the-internet.herokuapp.com/dropdown")
    
    page.select_option("#dropdown", label="Option 1")
    assert page.locator("#dropdown").input_value() == "1"
    
    page.select_option("#dropdown", label="Option 2")
    assert page.locator("#dropdown").input_value() == "2"


def test_dynamic_loading(page):
    page.goto("https://the-internet.herokuapp.com/dynamic_loading/1")
    
    page.click("button")
    
    # Playwright сам ждёт — не нужен WebDriverWait!
    page.wait_for_selector("#finish", state="visible")
    
    assert "Hello World!" in page.locator("#finish").inner_text()