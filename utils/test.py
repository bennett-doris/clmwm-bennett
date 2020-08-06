import requests
import json

origin = {
'lng': 116.3084202915042,
'lat': 40.05703033345938
}
destination = {
'lng': 116.30478278300266,
'lat': 40.05801181178359
}
ak = 'GcR4BkCh07kZPKupaiuktUlfRan6dzF9'

url = 'http://api.map.baidu.com/direction/v2/riding?'
# 起点经纬度，格式：纬度，经度；小数点后不超过六位
origin_lng = str(origin['lng'])
origin_lat = str(origin['lat'])
destination_lng = str(destination['lng'])
destination_lat = str(destination['lat'])
params = {
    'origin': origin_lat + ',' + origin_lng,
    'destination': destination_lat + ',' + destination_lng,
    'ak': ak
}
res = requests.get(url, params=params)
res.encoding = 'utf-8'
temp = json.loads(res.text)
print(temp)