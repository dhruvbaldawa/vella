from flask import Flask
from vella.logger import MongoLogger
from webapp.api import api


def create_app(config='dev'):
    app = Flask(__name__)
    cfg = {
        'dev': 'webapp.config.DevConfig',
        'test': 'webapp.config.TestConfig',
        'prod': 'webapp.config.Config',
    }
    app.config.from_object(cfg[config])
    app.register_blueprint(api)

    if app.debug:
        app.logger.debug('Config: {}'.format(cfg[config]))

    return app
