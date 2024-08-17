import serial
import re
#시리얼포트 객체 ser을 생성
#pc와 스위치 시리얼포트 접속정보
ser = serial.Serial(
    port = 'COM8', 
    baudrate=115200, 
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=8
    )

#시리얼포트 접속
ser.isOpen()

#시리얼포트 번호 출력
print(ser.name)

# 정규식 패턴
pattern = re.compile('^0x02.*0x03$')

stx = 2
stx = stx.to_bytes(1)
etx = 3
etx = etx.to_bytes(1)
# 정수를 바이트로 변환하여 전송
ser.write(stx + "asd".encode("utf-8") + etx)


# while True:
#     if ser.in_waiting > 0:  # 읽을 데이터가 있는지 확인
#         data = ser.readline().decode('utf-8').rstrip() # 데이터를 읽고 디코딩
#         # 정규식 매칭
#         if pattern.match(data):
#             dataSplit = data[4:-4].split(',')
#             if dataSplit[1] == '1':
#                 print(f"{dataSplit[0]}번 버스 요청")
#                 print(dataSplit[0].encode('utf-8'))
#             elif dataSplit[1] == '2':
#                 print(f"{dataSplit[0]}번 버스 헬프콜")
#             else:
#                 print(f"{dataSplit[0]}번 버스 요청 취소")


# # 사용이 끝나면 시리얼 포트를 닫습니다.
# ser.close()