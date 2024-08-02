import requests
import xmltodict

response = requests.get('http://openapitraffic.daejeon.go.kr/api/rest/arrive/getArrInfoByStopID?serviceKey=1n1TNpJ0Yl3dCAHm96RLhkh%2FnUXR0XqXtOkuoV4zf2u9a2R2dnLGQVUwk2MYyiCEyRHd9Y3u%2BJLMlq6ewbTSYA%3D%3D&BusStopID=8001378')    
dict_data = xmltodict.parse(response.text)
l = []
for i in dict_data['ServiceResult']['msgBody']['itemList']:
    l.append((i['ROUTE_NO'], i['EXTIME_MIN'], i['MSG_TP']))
l.sort()
for i in l:
    print(i)