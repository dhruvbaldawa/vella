import time
from urlparse import urlparse

from ..logger import Logger, InvalidDatabaseURL

from pymongo import MongoClient


## @FIXME: Move this to use MongoAlchemy
class MongoLogger(Logger):
    def __init__(self, url, **kwargs):
        hostname, db = self._parse_url(url)
        client = MongoClient(hostname, **kwargs)
        self._c = client[db]['logs']  # ALERT!

    def _parse_url(self, url):
        parsed_url = urlparse(url)
        if parsed_url.scheme != 'mongodb':
            raise InvalidDatabaseURL(url,
                                     'Invalid URL Scheme, should be "mongodb"')

        if not parsed_url.port:
            raise InvalidDatabaseURL(url,
                                     'Port not specified (default: 27017)')

        db = parsed_url.path[1:]  # remove the prefix '/'
        # reset the path and get rest of the hostname
        hostname = parsed_url._replace(path='').geturl()

        return hostname, db

    def log(self, kind, source, timestamp=None, description=None, **kwargs):
        if timestamp is None or not isinstance(timestamp, (int, float, long)):
            # maybe sanitize datetime objects sometime later and then
            # raise ValueError for incorrect time formats
            timestamp = time.time()

        doc = {
            '_id': self.generate_id(),
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

    def deactivate_log(self, doc_id):
        doc = self._c.find_one(doc_id)

        if 'active' in doc:
            del doc['active']
            self._c.save(doc)
