import json
import time
import requests

REST = "http://0.0.0.0:8000"
r = requests.get(REST)
print(r.json())

print("Configure...")
dict_data = {"value": 8}
data_json = json.dumps(dict_data)
r = requests.put(f"{REST}/detector/api/1.8.0/config/frame_time", data=data_json)
print(r.text)
r = requests.put(f"{REST}/detector/api/1.8.0/config/nimages", data=data_json)
print(r.text)


print("Arm...")
r = requests.put(f"{REST}/detector/api/1.8.0/command/arm")
print(r.json()["sequence id"])

print("Trigger...")
r = requests.put(f"{REST}/detector/api/1.8.0/command/trigger")
time.sleep(0.2)
r = requests.put(f"{REST}/detector/api/1.8.0/command/trigger")
time.sleep(0.2)
r = requests.put(f"{REST}/detector/api/1.8.0/command/trigger")
time.sleep(0.2)
r = requests.put(f"{REST}/detector/api/1.8.0/command/trigger")


print(r)

print("Disarm...")
r = requests.put(f"{REST}/detector/api/1.8.0/command/disarm")
print(r)
