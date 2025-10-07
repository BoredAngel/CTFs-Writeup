from flask import request

def log_request_info():
    print(f"[REQ] {request.remote_addr} -> {request.method} {request.path}")
