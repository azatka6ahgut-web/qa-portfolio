from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

class DropdownPage:
    URL = "https://the-internet.herokuapp.com/dropdown"

    DROPDOWN = (By.ID , "dropdown")

    def __init__(self,browser):
        self.browser=browser

    def open(self):
        self.browser.get(self.URL)
        return self
    
    def select_option(self, text):
        dropdown = Select(self.browser.find_element(*self.DROPDOWN))
        dropdown.select_by_visible_text(text)
        return self
    def get_selected_text(self):
        dropdown = Select(self.browser.find_element(*self.DROPDOWN))
        return dropdown.first_selected_option.text