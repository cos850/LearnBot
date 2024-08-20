from selenium.webdriver.common.by import By
from utils.driver_manager import DriverManager
from config.settings import URL_LOGIN, ID, PW
import time

def login():
    print('\n로그인 시작')
    driver = DriverManager.get_driver()
    
    try :
        # 웹 사이트 열기
        driver.get(URL_LOGIN)
        time.sleep(5)
        
        # iframe 전환
        loginIframe = driver.find_element(By.XPATH, '//iframe[@id="certframe"]')
        driver.switch_to.frame(loginIframe)

        # 법인 공인인증서 로그인 1단계 : ID 입력
        username_input = driver.find_element(By.ID, 'sub_common_id')
        login_id_button = driver.find_element(By.ID, 'login_common_btn')

        username_input.send_keys(ID)
        login_id_button.click()
        time.sleep(1)
        
        # 범용 공인인증서 로그인 2단계 : 공인인증서 비번 입력
        password_input = driver.find_element(By.ID, 'certPwd')
        login_pw_button = driver.find_element(By.XPATH, '//div[@class="pki-bottom"]/button[@class="btn-ok"]')
        
        password_input.send_keys(PW)
        login_pw_button.click()

        time.sleep(5) # 로그인 후 페이지 로드 대기
        print('로그인 성공')
    except Exception as e:
        raise RuntimeError('로그인 오류') from e
    finally:
        driver.switch_to.default_content()
        print('로그인 프로세스 종료')