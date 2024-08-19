from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import Config
import time

# 웹 드라이버 설정
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try :
    # 웹 사이트 열기
    driver.get(Config.login_url)
    time.sleep(5)

    # 법인 공인인증서 로그인 1단계 : ID 입력
    username_input = driver.find_element(By.XPATH, '//*[@id="sub_common_id"]')
    login_id_button = driver.find_element(By.XPATH, '//*[@id="login_common_btn"]')

    username_input.send_keys(Config.my_id)

    login_id_button.click()
    time.sleep(2)

    # 범용 공인인증서 로그인 2단계 : 공인인증서 비번 입력
    password_input = driver.find_element(By.ID, 'certPwd')
    password_input.send_keys(Config.my_pw)

    login_pw_button = driver.find_element(By.XPATH, '//div[@class="pki-bottom"]/button[@class="btn-ok"]')
    login_pw_button.click()

    # 로그인 후 페이지가 로드될 시간을 기다림
    time.sleep(5)  # 5초 대기, 필요에 따라 조정
finally:
    print(driver.page_source)
    time.sleep(20)
    driver.quit()