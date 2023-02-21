import requests

REST = "http://0.0.0.0:8000"

print("Configure...")
nimages = {"value": 1}
r = requests.put(f"{REST}/detector/api/1.8.0/config/nimages", json=nimages)
print(r.text)

print("Add user data")
user_data = {"value": {"sample_id": "my_sample"}}
r = requests.put(f"{REST}/stream/api/1.8.0/config/user_data", json=user_data)
print(r.text)

print("Arm...")
r = requests.put(f"{REST}/detector/api/1.8.0/command/arm")
print("sequence id:", r.json()["sequence id"])

print("Trigger...")
r = requests.put(f"{REST}/detector/api/1.8.0/command/trigger")


print("Disarm...")
r = requests.put(f"{REST}/detector/api/1.8.0/command/disarm")
print(r)
