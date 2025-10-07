from flask import Blueprint, request, redirect, Response
from helpers.ip_utils import is_local_ip
from helpers.token_utils import get_random_hex, allowedTab
import time

verify_bp = Blueprint('verify', __name__)

@verify_bp.route('/verifier')
def verifier():
    query = request.args.get('q')
    client_ip = request.remote_addr

    if is_local_ip(client_ip):
        for _ in range(20):
            if allowedTab.get(client_ip):
                return redirect(query)
            time.sleep(0.5)
        return "⏳ Verification timeout", 403

    return "hei, you sure you're not a bot?", 403

@verify_bp.route('/verify/<token>', methods=['GET'])
def verify(token):
    query = request.args.get('q')
    resp = query if query else get_random_hex(16)
    allowedTab[request.remote_addr] = token
    return Response(resp, mimetype='text/plain')
