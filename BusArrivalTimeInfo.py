# -*- coding: utf-8 -*-

import sys
import requests
import xmltodict
import time
import threading
import re
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QObject
from PyQt5 import QtWidgets, QtCore, QtGui
import serial
from pyqt_test import *

flag = 0
GlobalArriveInfoList = []

class ApiThread(QThread):
    update_arrive_info = pyqtSignal(list)

    def __init__(self, key, BusStopID):
        super().__init__()
        self.key = key
        self.BusStopID = BusStopID

    def run(self):
        while True:
            response = requests.get(f'http://openapitraffic.daejeon.go.kr/api/rest/arrive/getArrInfoByStopID?serviceKey={self.key}&BusStopID={self.BusStopID}')
            ArriveInfoDict = xmltodict.parse(response.text)
            ArriveInfoListBefore = []
            for ArriveInfo in ArriveInfoDict['ServiceResult']['msgBody']['itemList']:
                BusStopNm = '운행대기'
                RouteID = ''
                CarNM = ''
                #print(ArriveInfo)
                if ArriveInfo['MSG_TP'] != '07':
                    RouteID = ArriveInfo['ROUTE_CD']
                    CarNM = ArriveInfo['CAR_REG_NO']
                ArriveInfoListBefore.append([ArriveInfo['ROUTE_NO'], {
                    'ROUTE_NO': ArriveInfo['ROUTE_NO'],
                    'DESTINATION': ArriveInfo['DESTINATION'],
                    'EXTIME_MIN': ArriveInfo['EXTIME_MIN'],
                    'MSG_TP': ArriveInfo['MSG_TP'],
                    'BusStopNm': BusStopNm,
                    'CarNM': CarNM,
                    'RouteID': RouteID,
                    'isLowFloor': '0'
                }])
            ArriveInfoListBefore.sort()
            ArriveInfoList = [item[1] for item in ArriveInfoListBefore]

            for i in range(len(ArriveInfoList)):
                if len(ArriveInfoList[i]['ROUTE_NO']) == 1:
                    ArriveInfoList[i]['ROUTE_NO'] = '마을'+ArriveInfoList[i]['ROUTE_NO']
            
            while len(ArriveInfoList) % 5 != 0:
                ArriveInfoList.append({
                    'ROUTE_NO': '999', 'DESTINATION': '', 'EXTIME_MIN': '',
                    'MSG_TP': '', 'BusStopNm': '', 'CarNM': '', 'RouteID': '', 'isLowFloor': '0'
                })
            
            global GlobalArriveInfoList
            GlobalArriveInfoList = ArriveInfoList
            
            self.update_arrive_info.emit(ArriveInfoList)
            time.sleep(2)

class SerialThread(QThread):
    update_boarding_info = pyqtSignal(list)

    def __init__(self, serial_port, pageFlag):
        super().__init__()
        self.ser = serial.Serial(
            port=serial_port, 
            baudrate=115200, 
            parity='N',
            stopbits=1,
            bytesize=8,
            timeout=8
        )
        self.pageFlag = pageFlag
        self.BoardingNumList = []

    def run(self):
        pattern = re.compile('^0x02.*0x03$')
        global flag
        stx = 2
        stx = stx.to_bytes(1)
        etx = 3
        etx = etx.to_bytes(1)
        while True:
            if self.ser.in_waiting > 0:
                data = self.ser.readline().decode('utf-8').rstrip()
                print(data)
                if pattern.match(data):
                    dataSplit = data[4:-4].split(',')
                    idx = int(dataSplit[0]) + (5 * flag)
                    if dataSplit[1] == '1':
                        if idx not in self.BoardingNumList and idx < 6:  
                            self.BoardingNumList.append(idx)
                            print(idx, self.BoardingNumList)
                            txData = GlobalArriveInfoList[idx]['ROUTE_NO']
                            txData = txData.encode('utf-8')
                            self.ser.write(stx + txData + etx)
                    elif dataSplit[1] == '2':
                        self.BoardingNumList.append(idx)
                    else:
                        if idx in self.BoardingNumList:
                            self.BoardingNumList.remove(idx)
            self.update_boarding_info.emit(self.BoardingNumList)

class PageFlagThread(QThread):
    update_page_flag = pyqtSignal(int)

    def __init__(self, pageCnt):
        super().__init__()
        self.pageCnt = pageCnt
        self.pageFlag = 0

    def run(self):
        global flag
        while True:
            time.sleep(7)
            self.pageFlag = (self.pageFlag + 1) % self.pageCnt
            self.update_page_flag.emit(self.pageFlag)
            flag = self.pageFlag

class BusArrivalApp(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setupUi()
        
        self.now = datetime.now()
        
        self.key = ''
        self.BusStopID = ''
        self.ArriveInfoList = []
        self.pageFlag = 0
        self.BoardingNumList = []
        self.ADImageList = [
            'image/AD/1.png', 'image/AD/2.png', 'image/AD/3.png',
            'image/AD/4.png', 'image/AD/5.png'
        ]
        
        self.labelList = [{'Route': self.ui.label_2, 'Destination': self.ui.label_3, 'Minute': self.ui.label_4, 'Location': self.ui.label_5, 'Icon': self.ui.label_25},
                    {'Route': self.ui.label_6, 'Destination': self.ui.label_7, 'Minute': self.ui.label_8, 'Location': self.ui.label_9, 'Icon': self.ui.label_26},
                    {'Route': self.ui.label_10, 'Destination': self.ui.label_11, 'Minute': self.ui.label_12, 'Location': self.ui.label_13, 'Icon': self.ui.label_27},
                    {'Route': self.ui.label_14, 'Destination': self.ui.label_15, 'Minute': self.ui.label_16, 'Location': self.ui.label_17, 'Icon': self.ui.label_28},
                    {'Route': self.ui.label_18, 'Destination': self.ui.label_19, 'Minute': self.ui.label_20, 'Location': self.ui.label_21, 'Icon': self.ui.label_29}]
        self.BoardingUiList = [self.ui.label_32, self.ui.label_33, self.ui.label_34, self.ui.label_35]
        
        
        self.getInfo("info.txt")

        # QThreads
        self.api_thread = ApiThread(self.key, self.BusStopID)
        self.api_thread.update_arrive_info.connect(self.updateArriveInfo)
        self.api_thread.start()

        self.serial_thread = SerialThread('COM8', self.pageFlag)
        self.serial_thread.update_boarding_info.connect(self.updateBoardingInfo)
        self.serial_thread.start()

        self.page_flag_thread = PageFlagThread(len(self.ArriveInfoList)//5)
        self.page_flag_thread.update_page_flag.connect(self.updatePageFlag)
        self.page_flag_thread.start()

        self.updateAdsCnt = 0

        # GUI 업데이트를 위한 타이머
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateGui)
        self.timer.start(1000)  # 1초마다 업데이트

    def setupUi(self):
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.showMaximized()

    def getInfo(self, filename):
        with open(filename, 'r') as f:
            lines = f.readlines()
            d = {}
            for line in lines:
                a, b = line.split('=')
                d[a] = b.strip()
            self.key = d['key']
            self.BusStopID = d['BusStopID']

    def updateArriveInfo(self, ArriveInfoList):
        self.ArriveInfoList = ArriveInfoList
        self.page_flag_thread.pageCnt = len(self.ArriveInfoList)//5

    def updateBoardingInfo(self, BoardingNumList):
        self.BoardingNumList = BoardingNumList
        self.BoardingNumList.sort()
        
        for i in range(4):
            self.BoardingUiList[i].setText('')
        
        for i in range(len(self.BoardingNumList)):
            if self.ArriveInfoList[self.BoardingNumList[i]]['ROUTE_NO'] != '999':
                self.BoardingUiList[i].setText(self.ArriveInfoList[self.BoardingNumList[i]]['ROUTE_NO'])
            else:
                self.BoardingUiList[i].setText('')  

    def updatePageFlag(self, pageFlag):
        self.pageFlag = pageFlag

    def updateGui(self):
        self.now = datetime.now()
        self.ui.label_23.setText(f"{self.now.month}월 {self.now.day}일")
        self.ui.label_24.setText(f"{self.now.hour:02d}:{self.now.minute:02d}")
        
        for i in range(5):
            idx = i + (5 * self.pageFlag)
            if self.ArriveInfoList[idx]['ROUTE_NO'] == '999':
                self.clearRouteInfo(i)
            else:
                self.updateRouteInfo(i, idx)
        
        self.updateAds()
        self.updateNowArrive()

    def clearRouteInfo(self, i):
        self.labelList[i]['Route'].setText('')
        self.labelList[i]['Destination'].setText('')
        self.labelList[i]['Minute'].setText('')
        self.labelList[i]['Location'].setText('')

    def updateRouteInfo(self, i, idx):
        if self.ArriveInfoList[idx]['ROUTE_NO'][:2] == '마을' or len(self.ArriveInfoList[idx]['ROUTE_NO']) == 1:
            self.labelList[i]['Icon'].setPixmap(QtGui.QPixmap("image/asset/maeul.png"))
        else:
            self.labelList[i]['Icon'].setPixmap(QtGui.QPixmap("image/asset/not.png"))
        self.labelList[i]['Icon'].setScaledContents(True)
        self.labelList[i]['Route'].setText(self.ArriveInfoList[idx]['ROUTE_NO'])
        self.labelList[i]['Destination'].setText(self.ArriveInfoList[idx]['DESTINATION'])
        self.labelList[i]['Location'].setText(self.ArriveInfoList[idx]['BusStopNm'])
        if self.ArriveInfoList[idx]['MSG_TP'] == '07':
            self.labelList[i]['Minute'].setText('운행대기')
        elif self.ArriveInfoList[idx]['MSG_TP'] == '06':
            self.labelList[i]['Minute'].setText('진입중')
        elif int(self.ArriveInfoList[idx]['EXTIME_MIN']) <= 3:
            self.labelList[i]['Minute'].setText('잠시 후\n도착')
        else:
            self.labelList[i]['Minute'].setText(self.ArriveInfoList[idx]['EXTIME_MIN'] + '분')

    def updateAds(self):
        if self.updateAdsCnt == 0:
            self.ui.label_30.setPixmap(QtGui.QPixmap(self.ADImageList[0]))
            self.ui.label_30.setScaledContents(True)
            self.ui.label_31.setPixmap(QtGui.QPixmap(self.ADImageList[1]))
            self.ui.label_31.setScaledContents(True)
            self.ADImageList.append(self.ADImageList.pop(0))
        self.updateAdsCnt = (self.updateAdsCnt + 1) % 7

    def updateNowArrive(self):
        self.nowArriveList = []
        self.nowArriveStr = ' '.join(self.nowArriveList)
        self.ui.label_22.setText(self.nowArriveStr)

    def closeEvent(self, event):
        # 창을 닫을 때 모든 스레드를 안전하게 종료
        self.api_thread.quit()
        self.api_thread.wait()
        
        self.serial_thread.quit()
        self.serial_thread.wait()
        
        self.page_flag_thread.quit()
        self.page_flag_thread.wait()
        
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = BusArrivalApp()
    sys.exit(app.exec_())
