import requests
import xmltodict

key = 'thWTVZRkftwWDX%2F%2FBffYndD1kH0FA%2B9hrJ4tmX%2FTuFCKo00GOQ4qrPf0Qf5e0C83IRc5yPt%2F%2B6BM6X9n6P%2FSrQ%3D%3D'
BusStopID = '8001378'
response = requests.get('http://openapitraffic.daejeon.go.kr/api/rest/arrive/getArrInfoByStopID?serviceKey='+key+'&BusStopID='+BusStopID)    
dict_data = xmltodict.parse(response.text)
l = []
for i in dict_data['ServiceResult']['msgBody']['itemList']:
    l.append((i['ROUTE_NO'], i['EXTIME_MIN'], i['MSG_TP']))
l.sort()
for i in l:
    print(i)