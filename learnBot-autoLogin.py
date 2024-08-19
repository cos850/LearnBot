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
    
    # iframe 전환
    loginIframe = driver.find_element(By.XPATH, '//iframe[@id="certframe"]')
    driver.switch_to.frame(loginIframe)

    # 법인 공인인증서 로그인 1단계 : ID 입력
    username_input = driver.find_element(By.ID, 'sub_common_id')
    login_id_button = driver.find_element(By.ID, 'login_common_btn')

    username_input.send_keys(Config.my_id)
    login_id_button.click()
    time.sleep(1)
    
    # 범용 공인인증서 로그인 2단계 : 공인인증서 비번 입력
    password_input = driver.find_element(By.ID, 'certPwd')
    login_pw_button = driver.find_element(By.XPATH, '//div[@class="pki-bottom"]/button[@class="btn-ok"]')
    
    password_input.send_keys(Config.my_pw)
    login_pw_button.click()

    # 로그인 후 페이지가 로드될 시간을 기다림
    time.sleep(5)
    driver.switch_to.default_content()
except Exception as e:
    print('로그인 오류 발생!!!!!!!!')
    print(e)
    print(driver.page_source)
    driver.switch_to.default_content()
finally:
    print("프로그램 종료")
    time.sleep(20)
    driver.quit()