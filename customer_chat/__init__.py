import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'customer-chat.sqlite'),
        JWT_SECRET_KEY='dev'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import routes
    routes.configure_routes(app)

    jwt = JWTManager(app)

    from . import auth
    app.register_blueprint(auth.bp)

    return app


def create_socketio(app):
    from . import socketio
    s = SocketIO(app, cors_allowed_origins="*")
    socketio.configure_sockets(s)
    return s
