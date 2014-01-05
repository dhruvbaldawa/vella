from flask.ext.script import Manager, Server, prompt, prompt_pass
from flask import current_app as app
from webapp.app import create_app


manager = Manager(create_app)
manager.add_command('runserver', Server(host='0.0.0.0'))
manager.add_option('-c', '--config',
                   default='dev',
                   dest='config',
                   help='which configuration to load.')


@manager.command
def drop_db(all=False):
    print 'Dropping databases. ',
    if all:
        for collection in app.db.collection_names(False):
            app.db.drop_collection(collection)
    else:
        app.db.drop_collection('users')
    print 'Done.'


@manager.command
def create_db():
    print 'Creating databases. ',
    app.db.create_collection('users')
    print 'Done.'


@manager.command
def create_user(name='', username='', password=''):
    if not name:
        name = prompt('Enter name: ')
    if not username:
        username = prompt('Enter username: ')
    if not password:
        password = prompt_pass('Enter password: ')

    from webapp.api import register
    register(name, username, password)
    print 'User registered.'


if __name__ == '__main__':
    manager.run()
