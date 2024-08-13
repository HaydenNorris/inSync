import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_COOKIE_SECURE'] = True
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_SECRET_KEY'] = 'jwt-secret'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600

    JWTManager(app)

    # Import and register blueprints
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    db.init_app(app)
    with app.app_context():
        # now import the models from the models module
        from app.models import import_all_models
        import_all_models()
        db.create_all()

    return app
