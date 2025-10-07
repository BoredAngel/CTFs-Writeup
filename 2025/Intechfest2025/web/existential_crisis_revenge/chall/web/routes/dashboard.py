from flask import Blueprint, render_template
from middleware.auth_middleware import require_auth
import os

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
def dashboard_home():
    return render_template('dashboard.html', flag=os.getenv('FLAG2', 'flag{placeholder}'))
