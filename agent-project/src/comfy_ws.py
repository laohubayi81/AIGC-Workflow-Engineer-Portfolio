"""最小 WebSocket 客户端，只收 ComfyUI 的文本 JSON 帧。无第三方依赖。"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import socket
import threading
from typing import Callable
from urllib.parse import urlparse


def listen(base_url: str, client_id: str, on_msg: Callable[[dict], None], stop: threading.Event) -> None:
    u = urlparse(base_url)
    host = u.hostname or "127.0.0.1"
    port = u.port or (443 if u.scheme == "https" else 80)
    path = f"/ws?clientId={client_id}"
    key = base64.b64encode(os.urandom(16)).decode()
    s = socket.create_connection((host, port), timeout=10)
    s.settimeout(1.0)
    req = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        "\r\n"
    )
    s.sendall(req.encode())
    buf = b""
    while b"\r\n\r\n" not in buf:
        chunk = s.recv(4096)
        if not chunk:
            raise RuntimeError("WS handshake 被断开")
        buf += chunk
    head, rest = buf.split(b"\r\n\r\n", 1)
    if b"101" not in head.split(b"\r\n", 1)[0]:
        raise RuntimeError(f"WS handshake 失败: {head.split(b'\r\n', 1)[0]!r}")
    leftover = rest
    try:
        while not stop.is_set():
            try:
                msg, leftover = _read_text_frame(s, leftover, stop)
            except socket.timeout:
                continue
            if msg is None:
                break
            if not msg:
                continue
            try:
                on_msg(json.loads(msg))
            except json.JSONDecodeError:
                continue
    finally:
        try:
            s.close()
        except OSError:
            pass


def _read_text_frame(sock: socket.socket, leftover: bytes, stop: threading.Event) -> tuple[str | None, bytes]:
    data = leftover
    while len(data) < 2:
        if stop.is_set():
            return None, data
        chunk = sock.recv(4096)
        if not chunk:
            return None, data
        data += chunk
    b1 = data[1]
    ln = b1 & 0x7F
    off = 2
    if ln == 126:
        while len(data) < 4:
            chunk = sock.recv(4096)
            if not chunk:
                return None, data
            data += chunk
        ln = int.from_bytes(data[2:4], "big")
        off = 4
    elif ln == 127:
        while len(data) < 10:
            chunk = sock.recv(4096)
            if not chunk:
                return None, data
            data += chunk
        ln = int.from_bytes(data[2:10], "big")
        off = 10
    while len(data) < off + ln:
        if stop.is_set():
            return None, data
        chunk = sock.recv(4096)
        if not chunk:
            return None, data
        data += chunk
    payload = data[off : off + ln]
    rest = data[off + ln :]
    opcode = data[0] & 0x0F
    if opcode == 0x8:
        return None, rest
    if opcode == 0x1:
        return payload.decode("utf-8", errors="replace"), rest
    return "", rest
