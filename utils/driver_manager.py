from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class DriverManager:
    _driver = None

    @classmethod
    def get_driver(cls):
        if cls._driver is None:
            service = Service(ChromeDriverManager().install())
            cls._driver = webdriver.Chrome(service=service)
        return cls._driver

    @classmethod
    def quit_driver(cls):
        if cls._driver:
            cls._driver.quit()
            cls._driver = None
