import requests

response = requests.get('http://openapitraffic.daejeon.go.kr/api/rest/busposinfo/getBusPosByRtid?serviceKey=yVuOi%2FAuXdGyvr5hzlwJ37YvM9xxc17Cwdc7%2FR6d2ggfwB7rq0Q%2F9%2BOUQH0VOlODRFlgCizb%2FBKC3M1bnoYALA%3D%3D&busRouteId=30300001')
print(response.text)