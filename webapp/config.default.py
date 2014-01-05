class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = ''
    DB_URL = 'mongodb://localhost:27017/'
    DB_NAME = 'logs'


class DevConfig(Config):
    DEBUG = True
    DB_NAME = 'logs_dev'


class TestConfig(Config):
    DEBUG = True
    TESTING = True
    DB_NAME = 'logs_test'
