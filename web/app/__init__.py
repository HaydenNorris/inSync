import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO

db = SQLAlchemy()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    logging.basicConfig(level=logging.DEBUG)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    app.config['JWT_TOKEN_LOCATION'] = ["headers", "cookies"]
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 36000

    JWTManager(app)
    # set up CORS to allow all origins and accept cookies
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
    db.init_app(app)
    socketio.init_app(app, async_mode='eventlet', cors_allowed_origins="*")

    with app.app_context():
        # now import the models from the models module
        from app.models import import_all_models
        import_all_models()
        db.create_all()

    # Import and register blueprints
    from app.routes.player import player_routes
    from app.routes.game import game_routes
    from app.routes.socket import socket_routes
    from app.routes.clue import clue_routes
    app.register_blueprint(socket_routes)
    app.register_blueprint(player_routes)
    app.register_blueprint(game_routes)
    app.register_blueprint(clue_routes)


    # add seeders to app to be called from the command line
    # note to run these, you do not need to run the python interpreter,
    # simply execute the command in the terminal e.g. flask seed:users
    from app.seeders.scales import seed_scales
    from app.seeders.players import seed_players
    from app.seeders.games import seed_games
    from app.seeders.all import seed_all
    app.cli.add_command(seed_scales)
    app.cli.add_command(seed_players)
    app.cli.add_command(seed_games)
    app.cli.add_command(seed_all)


    return app
