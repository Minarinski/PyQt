# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\pyqt_test.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


#from PyQt5 import QtCore, QtGui, QtWidgets

import requests
import xmltodict
import time
import threading
import sys
import csv
from collections import defaultdict
sys.path.append('.')
from pyqt_test import *
from datetime import datetime
import pyttsx3
    
key = ''
BusStopID = ''
units = ["", "십", "백", "천"]
num_to_korean = ["", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]
engine = pyttsx3.init()
engine.setProperty('rate', 150)

def speak_text(text):
    engine.say(text)
    engine.runAndWait()

def number_to_korean(number_str):
    number_str = number_str.lstrip('0')  # 앞쪽의 0 제거
    if not number_str:
        return "영"
    return convert_section_to_korean(number_str)
    
def convert_section_to_korean(section):
    korean_section = []
    if section[0] == '마':
        korean_section.append("마을")
        section = section[2:]
    length = len(section)
    for i, num in enumerate(section):
        if num != '0':
            tmp = num_to_korean[int(num)] + units[length - i - 1] if int(num) != 1 or units[length - i - 1] == '' else units[length - i - 1]
            korean_section.append(tmp)
    return ''.join(korean_section)

def getInfo(filename):
    global key, BusStopID
    f = open(filename, 'r')
    lines = f.readlines()
    d = {}
    for line in lines:
        a,b = line.split('=')
        d[a] = b if b[-1] != '\n' else b[:-1]
    key = d['key']
    BusStopID = d['BusStopID']
    print(BusStopID, type(BusStopID), key, type(key))
    

def CallApi():
    global key, BusStopID
    pageFlag = False
    labelList = []
    labelList.append([ui.label_2, ui.label_3, ui.label_4, ui.label_5])
    labelList.append([ui.label_6, ui.label_7, ui.label_8, ui.label_9])
    labelList.append([ui.label_10, ui.label_11, ui.label_12, ui.label_13])
    labelList.append([ui.label_14, ui.label_15, ui.label_16, ui.label_17])
    labelList.append([ui.label_18, ui.label_19, ui.label_20, ui.label_21])
    #weekDayList = ['월', '화', '수', '목', '금', '토', '일']
    
    
    while True:
        now = datetime.now()
        ui.label_23.setText(str(now.month)+'월  '+str(now.day)+'일')
        ui.label_24.setText(str(now.hour)+':'+str(now.minute))
        
        response = requests.get('http://openapitraffic.daejeon.go.kr/api/rest/arrive/getArrInfoByStopID?serviceKey='+key+'&BusStopID='+BusStopID)    
        dict_data_arrive = xmltodict.parse(response.text)
        l = []
        print(dict_data_arrive)
        for i in dict_data_arrive['ServiceResult']['msgBody']['itemList']:
            BusStopNm = ''
            if 'LAST_STOP_ID' in i.keys():
                response = requests.get('http://openapitraffic.daejeon.go.kr/api/rest/stationinfo/getStationByUid?serviceKey='+key+'&arsId='+i['LAST_STOP_ID'])    
                dict_data_stationinfo = xmltodict.parse(response.text)
                if isinstance(dict_data_stationinfo['ServiceResult']['msgBody']['itemList'], dict):
                    BusStopNm = dict_data_stationinfo['ServiceResult']['msgBody']['itemList']['BUSSTOP_NM']
                else:
                    BusStopNm = dict_data_stationinfo['ServiceResult']['msgBody']['itemList'][0]['BUSSTOP_NM']
            else:
                BusStopNm = '운행대기'
            l.append([i['ROUTE_NO'], i['DESTINATION'],i['EXTIME_MIN'], i['MSG_TP'], BusStopNm])
        l.sort()
        if len(l) < 10:
            l.append(['999','0','0','0','0'])
            l.append(['999','0','0','0','0'])
            l.append(['999','0','0','0','0'])
            l.append(['999','0','0','0','0'])
            l.append(['999','0','0','0','0'])
        nowArriveList = []
        for i in range(5):
            print(l[i+(5*pageFlag)][0])
            if l[i+(5*pageFlag)][0] == '999':
                labelList[i][0].setText('')
                labelList[i][1].setText('')
                labelList[i][2].setText('')
                labelList[i][3].setText('')
            else:
                if len(l[i+(5*pageFlag)][0]) == 1:
                    l[i+(5*pageFlag)][0] = '마을'+l[i+(5*pageFlag)][0] 
                labelList[i][0].setText(l[i+(5*pageFlag)][0])
                if len(l[i+(5*pageFlag)][1]) < 7:
                    labelList[i][1].setText(l[i+(5*pageFlag)][1])
                else:
                    font = QtGui.QFont()
                    font.setFamily("나눔고딕 ExtraBold")
                    font.setPointSize(20)
                    font.setBold(True)
                    font.setWeight(75)
                    labelList[i][1].setFont(font)
                    labelList[i][1].setText(l[i+(5*pageFlag)][1])
                if l[i+(5*pageFlag)][3] == '07':
                    labelList[i][2].setStyleSheet("color: rgb(255, 255, 255);")
                    labelList[i][2].setText('운행대기')
                    labelList[i][3].setText('운행대기')
                elif l[i+(5*pageFlag)][3] == '06':
                    labelList[i][2].setStyleSheet("color: rgb(255, 0, 0);")
                    labelList[i][2].setText('진입중')
                    nowArriveList.append(l[i+(5*pageFlag)][0])
                    labelList[i][3].setText(l[i+(5*pageFlag)][4])
                else:
                    labelList[i][2].setStyleSheet("color: rgb(255, 255, 255);")
                    labelList[i][2].setText(l[i+(5*pageFlag)][2]+'분')
                    labelList[i][3].setText(l[i+(5*pageFlag)][4])
            
        nowArriveStr = ''
        for i in nowArriveList:
            nowArriveStr += i + '  '
        ui.label_22.setText(nowArriveStr)
        for i in nowArriveList:
            speak_text(number_to_korean(i)+"번 버스가 진입중입니다. 뒤로 한걸음 물러서 주세요.")
        pageFlag = not pageFlag
        time.sleep(7)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    
    Dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    getInfo("info.txt")
    thread = threading.Thread(target=CallApi)
    thread.daemon = True; thread.start()
    Dialog.showMaximized()
    sys.exit(app.exec_())
