from utils.driver_manager import DriverManager
from config.settings import URL_LOGIN
from features.auto_login import login
from features.auto_learn import learn
import time

def main():
    try :
        go_login_page(DriverManager.get_driver())
        login()
        learn()
    except Exception as e: 
        print(f"예외 종류: {e}")
    finally:
        print("프로그램 종료")
        DriverManager.quit_driver()

def go_login_page(driver):
    driver.get(URL_LOGIN)
    time.sleep(5)

if __name__ == "__main__":
    main()