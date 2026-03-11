import json

import zmq

ctx = zmq.Context()
s = ctx.socket(zmq.PULL)
s.connect("tcp://127.0.0.1:5555")

while True:
    parts = s.recv_multipart()
    hdr = json.loads(parts[0].decode())
    print(hdr.get("htype"), "parts=", len(parts))
