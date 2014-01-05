import uuid
import time
from pymongo import MongoClient


class MongoLogger(object):
    def __init__(self, url='mongodb://localhost:27017', db='logs'):
        client = MongoClient(url)
        self._c = client[db]['logs']  # ALERT!

    def _generate_id(self):
        return uuid.uuid4().hex

    def log(self, kind, source, timestamp=None, description=None, **kwargs):
        if timestamp is None or not isinstance(timestamp, (int, float, long)):
            # maybe sanitize datetime objects sometime later and then
            # raise ValueError for incorrect time formats
            timestamp = time.time()

        doc = {
            '_id': self._generate_id(),
            'kind': kind,
            'timestamp': timestamp,
            'source': source,
        }

        if description is not None:
            doc['description'] = description

        doc.update(kwargs)

        doc_id = self._c.insert(doc)
        return str(doc_id)

    def log_event(self, doc_id, event, timestamp=None, active=True, **kwargs):
        if timestamp is None or not isinstance(timestamp, (int, float, long)):
            # maybe sanitize datetime objects sometime later and then
            # raise ValueError for incorrect time formats
            timestamp = time.time()

        event = {
            'event': event,
            'timestamp': timestamp,
        }
        event.update(kwargs)

        doc = self._c.find_one(doc_id)

        if 'timeline' not in doc:
            doc['timeline'] = []

        doc['timeline'].append(event)
        # sort the timeline by timestamp
        doc['timeline'] = sorted(doc['timeline'], key=lambda x: x['timestamp'])

        doc['active'] = active
        # remove the active key if inactive
        if not active:
            del doc['active']

        self._c.save(doc)

    def get(self, doc_id_or_spec):
        return self._c.find_one(doc_id_or_spec)

    def deactivate_event(self, doc_id):
        doc = self._c.find_one(doc_id)

        if 'active' in doc:
            del doc['active']
            self._c.save(doc)
