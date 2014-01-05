from flask import Blueprint, request, jsonify
from flask import current_app as app
from flask.ext.login import UserMixin, login_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash


api = Blueprint('api', __name__, url_prefix='/api/v1')


class User(UserMixin):
    def __init__(self, id):
        self.id = id

    def is_active(self):
        return True

    def get_id(self):
        return self.id


def register(name, username, password):
    user = {
        '_id': username,  # short term hack for unique usernames
        'name': name,
        'username': username,
        'password': generate_password_hash(password),
    }
    app.db['users'].insert(user)  # ALERT!


@api.route('/login', methods=['POST'])
def login():
    '''
    Login view.

    :form str username:
    :form str password:
    '''
    username, password = request.form['username'], request.form['password']
    user = app.db['users'].find_one(username)  # ALERT!
    if user is not None and check_password_hash(user['password'], password):
        # login the user in.
        login_user(User(user['_id']))
        return jsonify({'name': user['name'], 'username': user['username']})
    else:
        return 'Invalid username/password', 401


@api.route('/log', methods=['POST'])
@login_required
def log():
    '''
    **Login required**
    Log something.
    '''
    return 'hello'
