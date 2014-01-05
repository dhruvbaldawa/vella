from flask import Flask
from webapp.api import api
from pymongo import MongoClient


def create_app(config='dev'):
    app = Flask(__name__)
    cfg = {
        'dev': 'webapp.config.DevConfig',
        'test': 'webapp.config.TestConfig',
        'prod': 'webapp.config.Config',
    }
    app.config.from_object(cfg[config])
    app.register_blueprint(api)

    configure_db(app)

    if app.debug:
        app.logger.debug('Config: {}'.format(cfg[config]))

    return app


def configure_db(app):
    app.db = MongoClient(app.config['DB_URL'])[app.config['DB_NAME']]
