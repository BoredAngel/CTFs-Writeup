from flask import Flask
from middleware.auth_middleware import require_auth
from routes.index import index_bp
from routes.auth import login_bp, register_bp, logout_bp
from routes.dashboard import dashboard_bp
from routes.verify import verify_bp
from middleware.logging_middleware import log_request_info
from helpers.jwt_helper import password

app = Flask(__name__)

# Middleware
app.before_request(log_request_info)
app.before_request(require_auth)
# Blueprints
app.register_blueprint(index_bp)
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(logout_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(verify_bp)

if __name__ == '__main__':
    print("Password "+password )
    app.run(host='0.0.0.0', port=1336, debug=False)
