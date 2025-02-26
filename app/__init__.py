from flask import Flask
from flask_jwt_extended import JWTManager
from .config import Config
from .db import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    jwt = JWTManager(app)
    init_db(app)

    from .routes.auth import auth_bp
    from .routes.verification import verification_bp
    from .routes.upload import upload_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(verification_bp, url_prefix='/verification')
    app.register_blueprint(upload_bp)  # Đăng ký upload blueprint

    return app