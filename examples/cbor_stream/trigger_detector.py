from uuid import uuid4

import requests

REST = "http://0.0.0.0:8000"

print(f"{'-' * 20} Configure stream format (cbor) {'-' * 20}")
r = requests.put(f"{REST}/stream/api/1.8.0/config/format", json={"value": "cbor"})

uuid = str(uuid4()).rsplit("-", maxsplit=1)[-1]
redis_key = f"eiger-frames-{uuid}"

print(f"{'-' * 20} Add user data {'-' * 20}")
# user_data = {"value": {"ordered_set_name": "sim-detector"}}
user_data = {"value": {"ordered_set_name": redis_key}}
r = requests.put(f"{REST}/stream/api/1.8.0/config/header_appendix", json=user_data)
print(r.text)

print(f"{'-' * 20} Configure number of images {'-' * 20}")
nimages = {"value": 1}
r = requests.put(f"{REST}/detector/api/1.8.0/config/nimages", json=nimages)
print(r.text)

print(f" {'-' * 20} Arm detector {'-' * 20}")
r = requests.put(f"{REST}/detector/api/1.8.0/command/arm")
print("sequence id:", r.json()["sequence id"])

for i in range(10):
    print(f"{'-' * 20} Change beam_center_x {'-' * 20}")
    beam_center_x = {"value": 1500}
    r = requests.put(
        f"{REST}/detector/api/1.8.0/config/beam_center_x", json=beam_center_x
    )
    print(r.text)

    print(f"{'-' * 20} Trigger detector {'-' * 20}")
    r = requests.put(f"{REST}/detector/api/1.8.0/command/trigger")
    print(r)

    print(f"{'-' * 20} Change beam_center_x {'-' * 20}")
    beam_center_x = {"value": 500}
    r = requests.put(
        f"{REST}/detector/api/1.8.0/config/beam_center_x", json=beam_center_x
    )
    print(r.text)

    print(f"{'-' * 20} Trigger detector {'-' * 20}")
    r = requests.put(f"{REST}/detector/api/1.8.0/command/trigger")
    print(r)

print(f"{'-' * 20} Disarm detector {'-' * 20}")
r = requests.put(f"{REST}/detector/api/1.8.0/command/disarm")
print(r)
