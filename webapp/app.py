from flask import Flask
from pymongo import MongoClient


def create_app(config='dev'):
    app = Flask(__name__)
    cfg = {
        'dev': 'webapp.config.DevConfig',
        'test': 'webapp.config.TestConfig',
        'prod': 'webapp.config.Config',
    }

    app.config.from_object(cfg[config])

    from webapp.api import api
    app.register_blueprint(api)

    configure_db(app)
    configure_extensions(app)

    if app.debug:
        app.logger.debug('Config: {}'.format(cfg[config]))

    return app


def configure_db(app):
    app.db = MongoClient(app.config['DB_URL'])[app.config['DB_NAME']]


def configure_extensions(app):
    from flask.ext.login import LoginManager
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(userid):
        from webapp.api import User
        return User(userid)
