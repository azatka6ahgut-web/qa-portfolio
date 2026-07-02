import pytest

# Не нужен свой fixture! pytest-playwright даёт page автоматически


def test_google_title(page):
    page.goto("https://google.com")
    assert "Google" in page.title()


def test_login_success(page):
    page.goto("https://the-internet.herokuapp.com/login")
    page.fill("#username", "tomsmith")
    page.fill("#password", "SuperSecretPassword!")
    page.click("button[type='submit']")
     # Ждём перехода на новую страницу
    page.wait_for_url("**/secure")
    assert "secure" in page.url

  

def test_checkboxes(page):
    page.goto("https://the-internet.herokuapp.com/checkboxes")
    checkboxes = page.locator("input[type='checkbox']")
    assert not checkboxes.nth(0).is_checked()
    assert checkboxes.nth(1).is_checked()
    checkboxes.nth(0).click()
    assert checkboxes.nth(0).is_checked()