from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = 'smartgadget_secret_2024'

    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    from app.routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)

    return app
