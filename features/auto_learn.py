from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from utils.driver_manager import DriverManager
from config.settings import COURSE_LIST, Course
from time import sleep
import copy
import traceback

driver: WebDriver = DriverManager.get_driver()
course_list = copy.deepcopy(COURSE_LIST)
current_course: Course = None

def learn():
    print('강의 수강 시작')
    try:
        global current_course
        options = driver.find_element(By.ID, 'Select_ApplCnt').find_elements(By.TAG_NAME, 'option')
        goCourseBtn = driver.find_element(By.ID, 'btnSelectApplCnt')
        
        for option in options :
            value = option.get_property('value')
            
            current_course = _find_course(value)
            if current_course == None : 
                print(f'[{option.text}] 과목에 대한 Course 정보를 찾을 수 없음. 해당 강의 스킵')
            else :
                print(f'[{option.text}] 과목의 학습 페이지로 이동합니다.')
                option.click()
                goCourseBtn.click()
                sleep(5)
                
                # 미완료 강의들 수강하기
                lectures = _find_uncompleted_lectures()
                
                # 확인용 임시 출력 ------
                print('수강할 목록: ') 
                for a_tag in lectures:
                    print(a_tag.find_element(By.TAG_NAME, 'b').text, ': ', a_tag.get_property('href'))
                print('===============')
                # -----------------------
                
                for lecture in lectures :
                    print(f'강의 듣기 시작 - {current_course.name}-{lecture.find_element(By.TAG_NAME, 'b').text}')
                    _play(lecture)
        
        print('모든 강의를 수강했습니다.')  
    except Exception as e:
        print("수강 오류")
        traceback.print_exc()
        raise


def _find_course(value):
    for course in course_list :
            if course.value == value : 
                return course


# 수강할 강의 목록 찾기
def _find_uncompleted_lectures():
    table = driver.find_element(By.ID, 'dataList')
    
    # 수강이 가능할 경우 a 태그가 있고, fontcolor가 '#588BA5'
    open_lectures = table.find_elements(By.XPATH, '//tbody//tr//td[@class="alignL"]//a[font[@color="#588BA5"]]')
    
    # 진행여부 열에 값이 '완료'인 경우는 제외
    return [lec for lec in open_lectures if not _isDone(lec)]

def _isDone(lecture):
    parent_tr = lecture.find_element(By.XPATH, '..').find_element(By.XPATH, '..')
    status_td = parent_tr.find_elements(By.TAG_NAME, 'td')[4]
    
    try :
        status_span = status_td.find_element(By.TAG_NAME, 'span')
        return status_span.text == '완료'
    except NoSuchElementException as e: 
        return False
    
    
# 강의 듣기
def _play(lecture: WebElement):
    main_window_handle = driver.current_window_handle
    
    try:
        lecture.click()
        sleep(3)
        
        # 학습 페이지가 새 창으로 띄워짐. 해당 window로 전환
        all_window_handles = driver.window_handles
        lecture_window_handle = [handle for handle in all_window_handles if handle != main_window_handle][-1]
        driver.switch_to.window(lecture_window_handle)
        
        driver.switch_to.frame('mainHaksup')    # 메인 학습 frame 내부로 전환
        _progress_all_step()                    # 강의 진행
        
        # 상단바 frame으로 전환 (학습 상태 확인 및 종료)
        driver.switch_to.default_content()
        driver.switch_to.frame('chkTime')
        
        # 학습 시간 충족 확인 및 대기
        is_time_fulfilled = _is_100_percent()
        while not is_time_fulfilled: 
            print(f'강의 수강 중.... [학습시간{_getPercent()}]')
            sleep(10*60) # 마지막 페이지에서 10분 기다리기
            is_time_fulfilled = _is_100_percent()
        print('학습 시간 충족. 해당 강의 학습을 종료합니다.')
        
        # 학습 종료 버튼 클릭
        driver.find_element(By.XPATH, '//div[@class="myStudy"]/p/a').click()
        
        # 학습을 종료하시겠습니까? -> 확인
        driver.switch_to.alert.accept() 
        
        # 종료하기 버튼 클릭
        driver.execute_script('StopStudy()')
        
        print('수강 완료')
    finally: 
        # 기존 창으로 돌아가기
        driver.switch_to.window(main_window_handle)
        sleep(2) # 페이지 재로딩 대기

def _progress_all_step():
    while True :
        isDone = _handle_alert()
        if isDone :
            return
        else :
            driver.find_element(By.XPATH, '//*[@id="title_frame"]/a[2]').click()
            sleep(1)    # 너무 빨리 누르지 않도록 대기

def _is_100_percent():
    return _getPercent() == ': 100%'

def _getPercent():
    my_study = driver.find_element(By.CLASS_NAME, 'myStudy')
    return my_study.find_element(By.ID, 'currentTime').text

def _handle_alert():
    try :
        alert = driver.switch_to.alert
        message = alert.text
        print(f'alert_message: {message}')
        alert.accept()
        
        if '평가하기의 모든 문제와 결과보기를 확인하고 진행해주세요' in message:
            _take_quiz()
        elif '마지막 페이지입니다' in message:
            return True
    except NoAlertPresentException : 
        return False
    return False

def _take_quiz():
    print('퀴즈 풀기')
    
    # 퀴즈 시작 버튼 클릭
    driver.find_element(By.XPATH, '//a[@id="startBtn"]').click()
    
    # 퀴즈 1~3 풀기
    for i in range(1, 4) :
        _selectAnswer(i)
        sleep(2)


def _selectAnswer(quiz_num):
    quiz_area = driver.find_element(By.ID, f'quiz_{quiz_num}')
    
    answer = quiz_area.find_element(By.ID, 'dap').get_property('value') # 정답 번호 가져오기
    print(f'quiz {quiz_num} - answer : {answer}')
    
    quiz_area.find_element(By.ID, f'a{answer}').click() # 정답 번호 클릭
    
    quiz_area.find_element(By.ID, 'answer_chk').click() # [확인] 버튼 클릭
    quiz_area.find_element(By.ID, 'next').click()       # [다음 문제/결과 확인] 버튼 클릭

