# app/__init__.py
from flask import Flask
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import config

def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    from app.routes.auth_routes  import auth_bp
    from app.routes.user_routes  import user_bp
    from app.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)

    return app