import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    app.config['JWT_TOKEN_LOCATION'] = ["headers", "cookies"]
    app.config['JWT_SECRET_KEY'] = 'jwt-secret'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600

    JWTManager(app)
    # set up CORS to allow all origins and accept cookies
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

    # Import and register blueprints
    from app.routes.user import user_routes
    from app.routes.game import game_routes
    app.register_blueprint(user_routes)
    app.register_blueprint(game_routes)

    db.init_app(app)
    with app.app_context():
        # now import the models from the models module
        from app.models import import_all_models
        import_all_models()
        db.create_all()

    # add seeders to app to be called from the command line
    # note to run these, you do not need to run the python interpreter,
    # simply execute the command in the terminal e.g. flask seed:users
    from app.seeders.scales import seed_scales
    from app.seeders.users import seed_players
    from app.seeders.games import seed_games
    from app.seeders.all import seed_all
    app.cli.add_command(seed_scales)
    app.cli.add_command(seed_players)
    app.cli.add_command(seed_games)
    app.cli.add_command(seed_all)


    return app
