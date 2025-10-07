from flask import Blueprint, request, redirect, make_response, render_template_string, jsonify
from helpers.jwt_helper import password as password_verify
from helpers.jwt_helper import create_token
from helpers.ip_utils import is_local_ip
import os
import re

login_bp = Blueprint('login', __name__)
register_bp = Blueprint('register', __name__)
logout_bp = Blueprint('logout', __name__)

@logout_bp.route('/logout', methods=['GET'])
def logout():
    resp = make_response(redirect('/login'))
    resp.set_cookie('auth', '', expires=0)
    return resp

@login_bp.route('/login', methods=['GET'])
def login_page():
    return render_template_string("""
    <form action="/api/login" method="post">
        Username: <input type="text" name="username"><br>
        Password: <input type="password" name="password"><br>
        <input type="submit" value="Login">
    </form>
    """)
    
@register_bp.route('/register', methods=['GET'])
def register_page():
    return render_template_string("""
    <form action="/api/register" method="post">
        Username: <input type="text" name="username"><br>
        Password: <input type="password" name="password"><br>
        <input type="submit" value="Register">
    </form>
    """)
    

@register_bp.route('/api/register', methods=['POST'])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not re.fullmatch(r"[a-z]{1,20}", username):
        return jsonify({"error": "Username invalid."}), 400
    return jsonify({"message": "Registration successful."}), 200




@login_bp.route('/api/login', methods=['POST', 'GET'])
def login():
    # any internal ip 
    # is_local_ip
    if not is_local_ip(request.remote_addr):
        print("Blocked login attempt from", request.remote_addr)
        return "Access denied", 403
    
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        if username == os.getenv("USERNAME", "longlonglonguser") and password in password_verify:
            token = create_token({'user': username})
            if isinstance(token, bytes):
                token = token.decode()
            resp = make_response('Login successful', 200)
            resp.set_cookie('auth', token, httponly=True)
            return resp
        else:
            return "Invalid credentials", 404
    elif request.method == 'GET':
        username = request.args.get("username")
        password = request.args.get("password")
        if username == os.getenv("USERNAME", "longlonglonguser") and password in password_verify:
            token = create_token({'user': username})
            if isinstance(token, bytes):
                token = token.decode()
            resp = make_response('Login successful', 200)
            resp.set_cookie('auth', token, httponly=True)
            return resp, 200
        else:
            return "Invalid credentials", 404
