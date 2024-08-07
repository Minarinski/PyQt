import requests
import xmltodict

key = ''
BusStopID = ''

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
    
getInfo('info.txt')

response = requests.get('http://openapitraffic.daejeon.go.kr/api/rest/arrive/getArrInfoByStopID?serviceKey='+key+'&BusStopID='+BusStopID)    
dict_data = xmltodict.parse(response.text)
l = []
for i in dict_data['ServiceResult']['msgBody']['itemList']:
    if i['MSG_TP'] != '07':
        if isinstance(i, dict):
            BusStopNm = i['ROUTE_CD']
            CarNM = i['CAR_REG_NO']
        else:
            BusStopNm = i[0]['ROUTE_CD']
            CarNM = i[0]['CAR_REG_NO']
        l.append([BusStopNm, CarNM])
print(len(l), len(dict_data['ServiceResult']['msgBody']['itemList']))
for i in l:
    response = requests.get('http://openapitraffic.daejeon.go.kr/api/rest/busreginfo/getBusRegInfoByRouteId?serviceKey='+key+'&busRouteId='+i[0])    
    dict_data = xmltodict.parse(response.text)
    for j in dict_data['ServiceResult']['msgBody']['itemList']:
        if j['CAR_REG_NO'] == i[1]:
            print(j['BUS_TYPE'])