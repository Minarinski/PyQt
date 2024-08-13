import pyttsx3
import threading
import time

l = []
lock = threading.Lock()  # Lock 객체 생성

def speak_text():
    global l
    while True:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        with lock:  # 리스트 접근을 Lock으로 보호
            if l:
                text = l.pop(0)
                engine.say(text)
                engine.runAndWait()
        time.sleep(0.1)  # CPU 점유를 줄이기 위해 sleep 추가

def test2():
    global l
    for i in range(1, 4):
        with lock:  # 리스트 접근을 Lock으로 보호
            l.append('안녕하세요')
        print(f'리스트에 추가됨: {l}')
        time.sleep(i * 2)

# 음성을 출력하는 스레드는 하나만 생성
thread1 = threading.Thread(target=speak_text)
thread1.daemon = True
thread1.start()

# 텍스트를 추가하는 스레드
thread2 = threading.Thread(target=test2)
thread2.daemon = True
thread2.start()

# 메인 프로그램이 종료되지 않도록 유지
try:
    while True:
        time.sleep(0.1)  # CPU 점유를 줄이기 위해 sleep 추가
except KeyboardInterrupt:
    print("프로그램이 종료되었습니다.")
