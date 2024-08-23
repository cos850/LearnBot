from typing import List
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from utils.driver_manager import DriverManager
from utils.learning import Course, Lecture
from config.settings import COURSE_LIST
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
        
        # TODO : option 개수를 맨 처음 받아와서 해당 개수만큼 반복
        # TODO : 탐색할 옵션 반환하는 함수를 통해 옵션 찾기 (찾다가 오류나면 다시 option 목록 가져오기 - StaleElementReferenceException)
        # TODO : 옵션이 반환된 경우 강의 수강 함수 실행
        
        course_options = driver.find_element(By.ID, 'Select_ApplCnt').find_elements(By.TAG_NAME, 'option')
        go_course_btn = driver.find_element(By.ID, 'btnSelectApplCnt')
        
        for option in course_options :
            value = option.get_property('value')
            
            current_course = _find_course(value)
            if current_course == None : 
                print(f'[{option.text}] 과목에 대한 Course 정보를 찾을 수 없음. 해당 강의 스킵')
            elif current_course.is_completed :
                print(f'[{current_course.name}] 과목은 이미 수강 완료되었습니다.')
            else :
                print(f'[{option.text}] 과목의 학습 페이지로 이동합니다.')
                option.click()
                go_course_btn.click()
                sleep(5)
                
                # 수강할 강의 목록 탐색
                lectures: List[Lecture] = _find_uncompleted_lectures()
                
                print(f'\n=== [{current_course.name}] 미수료 강의 목록 ===') 
                print('\n'.join(lecture.name for lecture in lectures))
                print('===========================================\n')
                
                for lecture in lectures :
                    print(f'[{current_course.name}] {lecture.name} 강의 수강 시작')
                    _play(lecture)
                    
                current_course.is_completed = True
                print(f'{current_course.name} 과목은 완료처리 되었습니다.')
        
        print('모든 강의를 수강했습니다.')  
    except Exception as e:
        print("수강 오류")
        traceback.print_exc()
        raise


def _find_course(value):
    for course in course_list :
            if course.value == value : 
                return course


def _find_uncompleted_lectures() -> List[Lecture]: 
    table = driver.find_element(By.ID, 'dataList')
    
    # 수강이 가능할 경우 a 태그가 있고, fontcolor가 '#588BA5'
    open_lectures = table.find_elements(By.XPATH, '//tbody//tr//td[@class="alignL"]//a[font[@color="#588BA5"]]')
    
    return [Lecture(lec.find_element(By.TAG_NAME, 'b').text, lec) for lec in open_lectures if not _isDone(lec)]

# 진행 여부 열이 '완료' 되어있는지 확인
def _isDone(lecture):
    parent_tr = lecture.find_element(By.XPATH, '..').find_element(By.XPATH, '..')
    status_td = parent_tr.find_elements(By.TAG_NAME, 'td')[4]
    
    try :
        status_span = status_td.find_element(By.TAG_NAME, 'span')
        return status_span.text == '완료'
    except NoSuchElementException as e: 
        return False
    
    
# 강의 듣기
def _play(lecture: Lecture):
    main_window_handle = driver.current_window_handle
    
    try:
        lecture.tag.click()
        sleep(3)
        
        # 학습 페이지가 새 창으로 띄워짐. 해당 window로 전환
        all_window_handles = driver.window_handles
        lecture_window_handle = [handle for handle in all_window_handles if handle != main_window_handle][-1]
        driver.switch_to.window(lecture_window_handle)
        
        _progress_all_step()
        
        _wait_until_100_percent()
        
        _close_lecture()
        
        print(f'{lecture.name} - 수강 완료')
    finally: 
        # 기존 창으로 돌아가기
        driver.switch_to.window(main_window_handle)
        sleep(2) # 페이지 재로딩 대기


# 강의 듣기
# 마지막 페이지라는 alert창이 뜰 때까지 진행
def _progress_all_step():
    driver.switch_to.frame('mainHaksup')
    try :
        while not _handle_alert() :
            driver.find_element(By.XPATH, '//*[@id="title_frame"]/a[2]').click()
            sleep(1)    # 너무 빨리 누르지 않도록 대기
    finally :
        driver.switch_to.default_content()


# 학습시간 100% 까지 대기
def _wait_until_100_percent():
    driver.switch_to.frame('chkTime')
    try :
        while not _getPercent() == ': 100%': 
            print(f'강의 수강 중.... [학습시간{_getPercent()}]')
            sleep(10*60) # 마지막 페이지에서 10분 기다리기
        print('학습 시간 충족. 해당 강의 학습을 종료합니다.')
    finally :
        driver.switch_to.default_content()

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

def _close_lecture() :
    driver.switch_to.frame('chkTime')

    # 학습 종료 버튼 클릭
    driver.find_element(By.XPATH, '//div[@class="myStudy"]/p/a').click()
    
    # 학습을 종료하시겠습니까? -> 확인
    driver.switch_to.alert.accept() 
    
    # 종료하기 버튼 클릭
    driver.switch_to.default_content()
    driver.switch_to.frame('mainHaksup')
    
    driver.execute_script('StopStudy()')

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
    print(f'{current_course.name} quiz {quiz_num} - answer : {answer}')
    
    quiz_area.find_element(By.ID, f'a{answer}').click() # 정답 번호 클릭
    
    quiz_area.find_element(By.ID, 'answer_chk').click() # [확인] 버튼 클릭
    quiz_area.find_element(By.ID, 'next').click()       # [다음 문제/결과 확인] 버튼 클릭

