#!/usr/bin/env python3
"""
Direct Blender WebSocket Client for GRAI Digital Twin Pipeline.
Connects directly to Blender's mcp_connector_v2.py on ws://127.0.0.1:9876
Executes Python code in Blender's runtime with full access to bpy.
"""
import sys
import socket
import base64
import json
import struct
import time

def send_to_blender(code, timeout=300.0):
    s = socket.socket()
    s.settimeout(timeout)
    s.connect(('127.0.0.1', 9876))

    # WebSocket Handshake
    key = base64.b64encode(b'grai_blender_bridge_16').decode()
    req = (
        f'GET / HTTP/1.1\r\n'
        f'Host: 127.0.0.1:9876\r\n'
        f'Upgrade: websocket\r\n'
        f'Connection: Upgrade\r\n'
        f'Sec-WebSocket-Key: {key}\r\n'
        f'Sec-WebSocket-Version: 13\r\n\r\n'
    )
    s.sendall(req.encode())
    s.recv(1024)

    # Frame WebSocket payload
    msg = json.dumps({'id': f'grai_{int(time.time()*1000)}', 'type': 'run_script', 'params': {'script': code}})
    data = msg.encode('utf-8')
    length = len(data)

    mask = b'\x47\x52\x41\x49'  # 'GRAI'
    header = bytearray([0x81])  # FIN + Text
    if length < 126:
        header.append(0x80 | length)
    elif length < 65536:
        header.append(0x80 | 126)
        header.extend(struct.pack('>H', length))
    else:
        header.append(0x80 | 127)
        header.extend(struct.pack('>Q', length))

    header.extend(mask)
    masked_data = bytearray(b ^ mask[i % 4] for i, b in enumerate(data))
    s.sendall(header + masked_data)

    # Read response header
    res_header = s.recv(2)
    res_len = res_header[1] & 0x7F
    if res_len == 126:
        res_len = struct.unpack('>H', s.recv(2))[0]
    elif res_len == 127:
        res_len = struct.unpack('>Q', s.recv(8))[0]

    payload = b''
    while len(payload) < res_len:
        chunk = s.recv(min(8192, res_len - len(payload)))
        if not chunk:
            break
        payload += chunk

    # Close WebSocket cleanly
    try:
        s.sendall(bytearray([0x88, 0x80]) + mask)
        s.close()
    except Exception:
        pass

    res = json.loads(payload.decode('utf-8'))
    if res.get('ok') == 1:
        return res.get('d', {}).get('out')
    else:
        raise RuntimeError(f"Blender Execution Error: {res.get('e')}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            code = f.read()
    else:
        code = sys.stdin.read()
    out = send_to_blender(code)
    print(out)
