from flask import Blueprint, render_template_string

index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def home():
    return render_template_string("""
    <h1>Welcome to Existential Crisis, im too lazy for building this frontend app. so here you go static html with backend by flask. heres your login page</h1>
    <a href="/login">Login</a>
    """)
