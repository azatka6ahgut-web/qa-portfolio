from selenium.webdriver.common.by import By


class CheckboxPage:
    URL = "https://the-internet.herokuapp.com/checkboxes"
    
    CHECKBOXES = (By.CSS_SELECTOR, "input[type='checkbox']")
    
    def __init__(self, browser):
        self.browser = browser
    
    def open(self):
        self.browser.get(self.URL)
        return self
    
    def get_checkboxes(self):
        return self.browser.find_elements(*self.CHECKBOXES)
    
    def is_checked(self, index):
        return self.get_checkboxes()[index].is_selected()
    
    def click_checkbox(self, index):
        self.get_checkboxes()[index].click()
        return self