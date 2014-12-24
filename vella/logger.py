import uuid


class Logger(object):
    def __init__(self, **kwargs):
        pass

    def generate_id(self):
        return uuid.uuid4().hex

    def log(self, kind, source, timestamp=None, description=None, **kwargs):
        raise NotImplementedError

    def log_event(self, doc_id, event, timestamp=None, active=True, **kwargs):
        raise NotImplementedError

    def get(self, doc_id_or_spec):
        raise NotImplementedError

    def deactivate_log(self, doc_id):
        raise NotImplementedError


class VLoggerError(Exception):
    def __init__(self, url, msg):
        self.url = url
        self.msg = msg

    def __str__(self):
        return '{}: {}'.format(self.msg, self.url)


class InvalidDatabaseURL(Exception):
    def __init__(self, url, msg='Invalid database URL'):
        self.url = url
        if msg is None:
            self.msg = 'Invalid database URL'

    def __str__(self):
        return '{}: {}'.format(self.msg, self.url)


class DatabaseError(Exception):
    pass
