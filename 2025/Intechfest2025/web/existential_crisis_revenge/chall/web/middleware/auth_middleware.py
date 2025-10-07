import os
from flask import request, redirect
from helpers.jwt_helper import password
from helpers.jwt_helper import decode_token

def require_auth():
    if request.path.startswith('/login') or request.path.startswith('/static'):
        return
    auth_cookie = request.cookies.get('auth')
    payload = decode_token(auth_cookie) if auth_cookie else None
    if not payload:
        usernameCookie = request.cookies.get('username')
        if usernameCookie == os.getenv("USERNAME", "longlonglonguser") and auth_cookie == password:
            payload = auth_cookie
    if request.path.startswith('/dashboard') and not payload:
        return redirect('/login')
