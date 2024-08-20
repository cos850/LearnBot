from utils.driver_manager import DriverManager
from features.auto_login import login

def main():
    try :
        DriverManager.get_driver()
        login()
    except Exception as e: 
        print(f"예외 종류: {e}")
    finally:
        print("프로그램 종료")
        DriverManager.quit_driver()

if __name__ == "__main__":
    main()