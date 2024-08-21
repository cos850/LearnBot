from typing import List
from selenium.webdriver.remote.webdriver import WebElement

class Course:
    is_completed = False
    uncompleted_studies: List[WebElement] = []
    
    def __init__(self, value, name):
        self.value = value
        self.name = name