import requests
import xmltodict
from BusInfoAdderPyQt import *
import serial
import serial.tools.list_ports

ui = Ui_Dialog()

serial_connection = None

def getBusInfo(busname, busrouteno):
    f = open('info.txt', 'r')
    lines = f.readlines()
    d = {}
    for line in lines:
        a,b = line.split('=')
        d[a] = b if b[-1] != '\n' else b[:-1]
    key = d['key']
    BusRouteID = ''
    for idx in range(1,3):
        response = requests.get('http://openapitraffic.daejeon.go.kr/api/rest/busRouteInfo/getRouteInfoAll?serviceKey=Ya0Uj6qkt89wuBdfOjb1XMsBeY3iH8Rq8Mee9Luexx%2FNtfsc5%2F8eMZaNncY0Lo5lHFBKEayysnCd%2FKo4PxX5gg%3D%3D&reqPage='+str(idx))  
        dict_data = xmltodict.parse(response.text)

        for i in dict_data['ServiceResult']['msgBody']['itemList']:
            if i['ROUTE_NO'] == busrouteno:
                BusRouteID = i['ROUTE_CD']
                break
    print(BusRouteID)
    response = requests.get('http://openapitraffic.daejeon.go.kr/api/rest/busRouteInfo/getStaionByRoute?serviceKey='+key+'&busRouteId='+BusRouteID)    
    dict_data = xmltodict.parse(response.text)
    l = []
    for i in dict_data['ServiceResult']['msgBody']['itemList']:
        l.append([busname, busrouteno, i['BUS_STOP_ID'], i['GPS_LATI'], i['GPS_LONG']])
    
    for i in l:
        print(i)
            

def populate_ports():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        ui.PortCombo.addItem(port.device)

def populate_baudrates():
    baudrates = [9600, 115200, 248000]
    for baudrate in baudrates:
        ui.BaudrateCombo.addItem(str(baudrate))

def open_serial():
    global serial_connection
    port = ui.PortCombo.currentText()
    baudrate = ui.BaudrateCombo.currentText()
    if port and baudrate:
        try:
            serial_connection = serial.Serial(port, baudrate)
            ui.IsOpenLabel.setText("연결 되었습니다.")
        except Exception as e:
            ui.IsOpenLabel.setText("연결 실패: {}".format(str(e)))

def close_serial():
    if serial_connection and serial_connection.is_open:
        serial_connection.close()
        ui.IsOpenLabel.setText("연결이 끊어졌습니다.")

def print_bus_route():
    if serial_connection:
        bus_route_no = ui.BusRouteNoInput.text()
        bus_name = ui.BusNMInput.text()
        print("Bus Route No:", bus_route_no)
        print("Bus Name:", bus_name)
        getBusInfo(bus_name, bus_route_no)
    else:
        print('serial not open!!!!!!!')
    


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui.setupUi(Dialog)
    Dialog.show()
    populate_ports()
    populate_baudrates()
    ui.OpenBtn.clicked.connect(open_serial)
    ui.CloseBtn.clicked.connect(close_serial)
    ui.BusRouteBtn.clicked.connect(print_bus_route)
    sys.exit(app.exec_())
