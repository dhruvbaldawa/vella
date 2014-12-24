import time
import logging

from urlparse import urlparse

from ..logger import Logger, InvalidDatabaseURL, DatabaseError

from sqlalchemy import (create_engine, Column, String, Float, Text)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
logger = logging.getLogger(__name__)


class Log(Base):
    __tablename__ = 'logs'  # ALERT!

    id = Column(String(50), primary_key=True, autoincrement=False)
    kind = Column(String(255), nullable=False)
    description = Column(Text())
    _document = Column('document', JSONB(), nullable=False)
    source = Column(String(255), nullable=False)
    timestamp = Column(Float(default=lambda: time.time()), nullable=False)

    @property
    def document(self):
        d = {}
        d.update(self._document)
        d.update({
            'kind': self.kind,
            'id': self.id,
            'description': self.description,
            'source': self.source,
            'timestamp': self.timestamp,
        })
        return d

    @document.setter
    def document(self, document):
        for field in ['id', 'kind', 'description', 'source', 'timestamp']:
            if field in document:
                setattr(self, field, document[field])
                del document[field]
        self._document = document


class PostgresLogger(Logger):
    def __init__(self, url, **kwargs):
        self._verify_url(url)
        self._engine = create_engine(url, **kwargs)

        self._verify_database()

        Session = sessionmaker(bind=self._engine)
        self.session = Session()

    def _verify_database(self):
        major, minor, _ = self._engine.dialect.server_version_info
        if not (major >= 9 and minor >= 4):
            raise DatabaseError('Incompatible version of database found '
                                'should be >= 9.4 and found {}.{}'
                                .format(major, minor))

        if self._engine.has_table('logs'):  # ALERT!
            Base.metadata.create_all()

    def _verify_url(self, url):
        parsed_url = urlparse(url)
        if parsed_url.scheme != 'postgresql':
            raise InvalidDatabaseURL(url,
                                     'Invalid URL Scheme, '
                                     'should be "postgresql"')

    def log(self, kind, source, timestamp=None, description=None, **kwargs):
        if timestamp is None or not isinstance(timestamp, (int, float, long)):
            # maybe sanitize datetime objects sometime later and then
            # raise ValueError for incorrect time formats
            timestamp = time.time()

        log = Log(
            id=self.generate_id(),
            kind=kind,
            timestamp=timestamp,
            source=source,
        )

        if description is not None:
            log.description = description

        log.data = kwargs

        # @TODO: add robust saving mechanism
        self.session.add(log)
        self.session.commit()

        return log.id

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
