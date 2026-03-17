import requests

REST = "http://0.0.0.0:8000"

print(f"{'-' * 20} Configure stream format (legacy) {'-' * 20}")
r = requests.put(f"{REST}/stream/api/1.8.0/config/format", json={"value": "legacy"})

r = requests.put(f"{REST}/stream/api/1.8.0/config/mode", json={"value": "enabled"})
print("stream enabled:", r.text)

r = requests.put(
    f"{REST}/stream/api/1.8.0/config/header_detail", json={"value": "basic"}
)
print("header detail:", r.text)


print(f"{'-' * 20} Configure number of images {'-' * 20}")
nimages = {"value": 1}
r = requests.put(f"{REST}/detector/api/1.8.0/config/nimages", json=nimages)
print(r.text)

# TODO: the user data may have to be a string for the legacy stream, not dict
print(f"{'-' * 20} Add user data {'-' * 20}")
user_data = {
    "value": {
        "acquisition_uuid": "123e4567-e89b-12d3-a456-426614174000",
    }
}
r = requests.put(f"{REST}/stream/api/1.8.0/config/header_appendix", json=user_data)
print(r.text)

print(f" {'-' * 20} Arm detector {'-' * 20}")
r = requests.put(f"{REST}/detector/api/1.8.0/command/arm")
print("sequence id:", r.json()["sequence id"])

print(f"{'-' * 20} Trigger detector {'-' * 20}")
r = requests.put(f"{REST}/detector/api/1.8.0/command/trigger")
print(r)


print(f"{'-' * 20} Disarm detector {'-' * 20}")
r = requests.put(f"{REST}/detector/api/1.8.0/command/disarm")
print(r)
