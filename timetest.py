from urllib.request import urlopen
import json
from datetime import datetime

res = urlopen('http://worldtimeapi.org/api/timezone/America/Vancouver')
result = res.read().strip()
result_str = result.decode('utf-8')
result_json = json.loads(result_str)
datetime_str = result_json['datetime']
time = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f%z')

print(time.hour)