import hashlib
import random
import string


def _random_string():
    # generate a random string of 5 - 15 characters
    return ''.join(random.sample(string.ascii_letters + string.punctuation,
                                 random.randrange(5, 15)))


class Logger(object):
    def __init__(self, **kwargs):
        pass

    def generate_id(self, id=None):
        if id is None:
            id = _random_string()
        return hashlib.sha256(id).hexdigest()

    def log(self, kind, id=None, source=None, timestamp=None, **kwargs):
        raise NotImplementedError

    def log_event(self, id, event, timestamp=None, active=True, **kwargs):
        raise NotImplementedError

    def get(self, id):
        raise NotImplementedError

    def deactivate_log(self, id):
        raise NotImplementedError


class VLoggerError(Exception):
    def __init__(self, url, msg):
        self.url = url
        self.msg = msg

    def __str__(self):
        return '{}: {}'.format(self.msg, self.url)


class InvalidDatabaseURL(VLoggerError):
    def __init__(self, url, msg='Invalid database URL'):
        super(InvalidDatabaseURL, self).__init__(url, msg)

    def __str__(self):
        return '{}: {}'.format(self.msg, self.url)


class DatabaseError(Exception):
    pass
