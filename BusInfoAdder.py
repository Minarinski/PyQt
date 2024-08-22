import requests
import xmltodict

key = ''
BusRouteID = ''

def getInfo(filename):
    global key, BusRouteID
    f = open(filename, 'r')
    lines = f.readlines()
    d = {}
    for line in lines:
        a,b = line.split('=')
        d[a] = b if b[-1] != '\n' else b[:-1]
    key = d['key']
    BusRouteID = d['BusRouteID']
    
getInfo('info.txt')

response = requests.get('http://openapitraffic.daejeon.go.kr/api/rest/busRouteInfo/getStaionByRoute?serviceKey='+key+'&busRouteId='+BusRouteID)    
dict_data = xmltodict.parse(response.text)
l = []
for i in dict_data['ServiceResult']['msgBody']['itemList']:
    print(i['BUS_STOP_ID'], i['GPS_LATI'], i['GPS_LONG'])