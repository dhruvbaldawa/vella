import json

from flask import Blueprint, request, jsonify
from flask import current_app as app
from flask.ext.login import UserMixin, login_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash

from vella.logger import MongoLogger


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


def _get_logger():
    return MongoLogger(app.config['DB_URL'], app.config['DB_NAME'])


@api.route('/login', methods=['POST'])
def login():
    '''
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

    :form str kind:
    :form str source:
    :form int/float timestamp optional:
    :form str description optional:
    :form json other optional:
    '''
    logger = _get_logger()
    log = {
        'kind': request.form['kind'],
        'source': request.form['source'],
        'timestamp': request.form.get('timestamp', None),
        'description': request.form.get('description', None),
    }
    log.update(json.loads(request.form.get('other', '{}')))
    doc_id = logger.log(**log)

    return jsonify({'doc_id': doc_id})


@api.route('/log/<doc_id>', methods=['GET'])
@login_required
def get_log(doc_id):
    '''
    ** Login required **

    :param doc_id:
    '''
    logger = _get_logger()
    doc = logger.get(doc_id)
    if doc is not None:
        return jsonify(doc)
    else:
        return jsonify({'error': 'The specified document was not found.'}), 404
