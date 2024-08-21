from selenium.webdriver.remote.webdriver import WebElement

class Course:
    is_completed = False
    
    def __init__(self, value, name):
        self.value = value
        self.name = name
        
class Lecture:
    def __init__(self, name, tag: WebElement):
        self.name = name
        self.tag = tag