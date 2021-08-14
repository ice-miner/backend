import requests
import json
from influxdb import InfluxDBClient
import time
import geohash

client = InfluxDBClient(host='localhost', port=8086, username='admin', password='admin')
client.switch_database("db0")

while True:
    try:
        data = json.loads(requests.get("https://iceportal.de/api1/rs/status").text)
    except requests.exceptions.ConnectionError as e:
        print(e)
        time.sleep(1)
    geo = geohash.encode(data["latitude"], data["longitude"])
    json_body = [
    {
        "measurement": "ICE",
        "tags": {
            "tzn": data["tzn"],
        },
        "fields": {
            #"connection": data["connection"],
            #"serviceLevel": data["serviceLevel"],
            #"gpsStatus   ": data["gpsStatus   "],
            #"internet": data["internet"],
            "latitude": data["latitude"],
            "longitude": data["longitude"],
            #"tileY": data["tileY"],
            #"tileX": data["tileX"],
            #"series": data["series"],
            #"serverTime": data["serverTime"],
            "speed": data["speed"],
            "geohash": geo
            #"trainType": data["trainType"],
            #"tzn": data["tzn"],
            #"wagonClass": data["wagonClass"],
            #"connectivity": data["connectivity"],
            #"bapInstalled": data["bapInstalled"]
        }
    }]
    client.write_points(json_body)
    print(f"logged {json_body}")
    time.sleep(5)