import serial
import time

# 시리얼 포트와 보드레이트를 설정합니다.
ser = serial.Serial('COM5', 9600)  # 'COM3'을 실제 아두이노가 연결된 포트로 변경하세요.

try:
    while True:
        # "hah" 문자열을 시리얼 포트로 보냅니다.
        ser.write(b'hah')
        print("Sent: hah")
        # 1초 동안 대기합니다.
        time.sleep(1)
except KeyboardInterrupt:
    # 프로그램이 종료될 때 시리얼 포트를 닫습니다.
    ser.close()
    print("Serial port closed")
