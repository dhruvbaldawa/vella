from flask import Blueprint, request


api = Blueprint('api', __name__, url_prefix='/api/v1')


@api.route('/login', methods=['POST'])
def login():
    username, password = request.form['username'], request.form['password']
    return username, password
