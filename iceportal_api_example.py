from flask import Flask, jsonify
import json

status_json = dict(json.loads(open("example_status.json", "r").read()))
trip_json = dict(json.loads(open("example_trip.json", "r").read()))

app = Flask(__name__)

@app.route("/status")
def status():
    return jsonify(status_json)

@app.route("/trip")
def trip():
    return jsonify(trip_json)

if __name__ == '__main__':    app.run(debug = True,host="0.0.0.0")