import uuid
import time
from pymongo import MongoClient


class Logger(object):
    def __init__(self, url='mongodb://localhost:27017', db='logs', session=None):
        client = MongoClient(url)
        self._c = client[db]['logs']  # ALERT!

    def _generate_id(self):
        return uuid.uuid4().hex

    def log(self, kind, source, timestamp=None, description=None, extra=None):
        if timestamp is None or not isinstance(time, (int, float, long)):
            timestamp = time.time()

        doc = {
            '_id': self._generate_id(),
            'kind': kind,
            'timestamp': timestamp,
            'source': source,
        }

        if description is not None:
            doc['description'] = description

        if extra is not None:
            doc['extra'] = extra

        doc_id = self._c.insert(doc)
        return str(doc_id)

    def add_to_timeline():
        pass

    def in_progress():
        pass
