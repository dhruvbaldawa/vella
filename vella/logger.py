import hashlib
import random
import string


def _random_string():
    # generate a random string of 5 - 15 characters
    return ''.join(random.sample(string.ascii_letters + string.punctuation,
                                 random.randrange(5, 15)))


class Logger(object):
    def __init__(self, **kwargs):
        pass  # pragma: no cover

    def generate_id(self, id=None):
        if id is None:
            id = _random_string()
        # HACK to differentiate hashes from actual plugin supplied
        # ids, so when a plugin calls logger.log_event(somestring), it
        # should work with both hash and plugin supplied ids, assuming
        # plugin supplied ids should *not* start with $
        return "$" + hashlib.sha256(id).hexdigest()

    def get_db_id(self, id):
        if id is not None and id.startswith("$"):
            return id
        else:
            return self.generate_id(id)

    def log(self, kind, id=None, source=None, timestamp=None, **kwargs):
        raise NotImplementedError  # pragma: no cover

    def log_event(self, id, event, timestamp=None, active=True, **kwargs):
        raise NotImplementedError  # pragma: no cover

    def get(self, id):
        raise NotImplementedError  # pragma: no cover

    def deactivate_log(self, id):
        raise NotImplementedError  # pragma: no cover


class VLoggerError(Exception):
    def __init__(self, url, msg):
        self.url = url
        self.msg = msg

    def __str__(self):
        return '{}: {}'.format(self.msg, self.url)  # pragma: no cover


class InvalidDatabaseURL(VLoggerError):
    def __init__(self, url, msg='Invalid database URL'):
        super(InvalidDatabaseURL, self).__init__(url, msg)


class DatabaseError(Exception):
    pass
