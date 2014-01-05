class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'l"\xe4\x10D\xbc9fw\t\x060\r;\xaa\xd66_:Bs\x0c|\xc6'
    DB_URL = 'mongodb://localhost:27017/'
    DB_NAME = 'logs'


class DevConfig(Config):
    DEBUG = True
    DB_NAME = 'logs_dev'


class TestConfig(Config):
    DEBUG = True
    TESTING = True
    DB_NAME = 'logs_test'
