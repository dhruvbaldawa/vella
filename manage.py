from flask.ext.script import Manager, Server
from webapp.app import create_app


manager = Manager(create_app)
manager.add_command('runserver', Server(host='0.0.0.0'))
manager.add_option('-c', '--config',
                   default='dev',
                   dest='config',
                   help='which configuration to load.')


if __name__ == '__main__':
    manager.run()
