import requests
import json
#from influxdb import InfluxDBClient
import time
#import geohash
import requests
from Crypto.PublicKey import RSA
from hashlib import sha512
from datetime import datetime

#client = InfluxDBClient(host='localhost', port=8086, username='admin', password='admin')
#client.switch_database("db0")

with open("private.pem", "r") as f:
    key = RSA.import_key(f.read())

while True:
    try:
        data = json.loads(requests.get("https://iceportal.de/api1/rs/status").text)
    except requests.exceptions.ConnectionError as e:
        print(e)
        time.sleep(1)


    body = f'''{{
    "timestamp": "{datetime.fromtimestamp(data["serverTime"]/1000).strftime("%Y-%m-%dT%H:%M:%S")}",
    "connection": "{data["connection"]}",
    "serviceLevel": "{data["serviceLevel"]}",
    "gpsStatus": "{data["gpsStatus"]}",
    "internet": "{data["internet"]}",
    "latitude": {data["latitude"]},
    "longitude": {data["longitude"]},
    "series": "{data["series"]}",
    "speed": {data["speed"]},
    "trainType": "{data["trainType"]}",
    "tzn": "{data["tzn"]}"
    }}'''

    body_bytes = bytes(body, "utf-8")
    hash = int.from_bytes(sha512(body_bytes).digest(), byteorder='big')
    signature = pow(hash, key.d, key.n)

    req = requests.post(f"http://195.201.25.135:8000/traindata",data=body, headers={"signature": str(signature)})
    print(req.request.url)
    print(req.text)
    print(f"logged {body}")
    time.sleep(5)