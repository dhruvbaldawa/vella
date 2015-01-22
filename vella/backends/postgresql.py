import time
import logging

from urlparse import urlparse

from ..logger import Logger, InvalidDatabaseURL, DatabaseError

from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import scoped_session, sessionmaker


Base = declarative_base()
logger = logging.getLogger(__name__)


class Log(Base):
    __tablename__ = 'logs'  # ALERT!

    id = Column(String(65), primary_key=True, autoincrement=False)
    kind = Column(String(255), nullable=False)
    _document = Column('document', MutableDict.as_mutable(JSONB),
                       nullable=False)
    source = Column(String(255), nullable=True)
    timestamp = Column(Float(default=lambda: time.time()), nullable=False)

    @property
    def document(self):
        d = MutableDict()
        d.update(self._document)
        d.update({
            'kind': self.kind,
            'id': self.id,
            'source': self.source,
            'timestamp': self.timestamp,
        })
        return d

    @document.setter
    def document(self, document):
        for field in ['id', 'kind', 'source', 'timestamp']:
            if field in document:
                setattr(self, field, document[field])
                del document[field]
        self._document = document


class PostgresqlLogger(Logger):
    def __init__(self, url, **kwargs):
        self._verify_url(url)
        self._engine = create_engine(url, **kwargs)

        self._verify_database()

        # Session = sessionmaker(bind=self._engine, autocommit=True)
        Session = scoped_session(sessionmaker(bind=self._engine,
                                              autocommit=True))
        self.session = Session()

    def _verify_database(self):
        major, minor, _ = self._engine.dialect._get_server_version_info(self._engine)
        if not (major >= 9 and minor >= 4):
            raise DatabaseError('Incompatible version of database found '
                                'should be >= 9.4 and found {}.{}'
                                .format(major, minor))

        if self._engine.has_table('logs'):  # ALERT!
            Base.metadata.create_all(self._engine)

    def _verify_url(self, url):
        parsed_url = urlparse(url)
        if parsed_url.scheme != 'postgresql':
            raise InvalidDatabaseURL(url,
                                     'Invalid URL Scheme, '
                                     'should be "postgresql"')

    def log(self, kind, id=None, source=None, timestamp=None,
            update_existing=False, **kwargs):
        if timestamp is None or not isinstance(timestamp, (int, float, long)):
            # maybe sanitize datetime objects sometime later and then
            # raise ValueError for incorrect time formats
            timestamp = time.time()

        id = self.get_db_id(id)
        log = Log(
            id=id,
            kind=kind,
            timestamp=timestamp,
            source=source,
        )

        log.document = kwargs

        # @TODO: add robust saving mechanism
        try:
            self.session.begin()
            self.session.add(log)
            self.session.commit()
        except:
            self.session.rollback()
            raise

        return log.id

    def log_event(self, id, event, timestamp=None, active=True, **kwargs):
        if timestamp is None or not isinstance(timestamp, (int, float, long)):
            # maybe sanitize datetime objects sometime later and then
            # raise ValueError for incorrect time formats
            timestamp = time.time()

        event = {
            'event': event,
            'timestamp': timestamp,
        }
        event.update(kwargs)

        # @TODO: add robustness
        id = self.get_db_id(id)
        doc = self.session.query(Log).filter(Log.id == id).one()

        if 'timeline' not in doc.document:
            doc._document['timeline'] = []

        doc._document['timeline'].append(event)
        # sort the timeline by timestamp
        doc._document['timeline'] = sorted(doc.document['timeline'],
                                           key=lambda x: x['timestamp'])

        doc._document['active'] = active
        # remove the active key if inactive
        if not active:
            del doc._document['active']

        # @TODO: add robust saving mechanism
        try:
            self.session.begin()
            self.session.add(doc)
            self.session.commit()
        except:
            self.session.rollback()
            raise

    def _get(self, id):
        id = self.get_db_id(id)
        # @TODO: just throw this out of the window or do something better!
        if isinstance(id, basestring):
            # @TODO: add robustness
            return self.session.query(Log).filter(Log.id == id).one()

    def get(self, id):
        return self._get(id).document

    def deactivate_log(self, id):
        id = self.get_db_id(id)
        # @TODO: add robustness
        doc = self.session.query(Log).query.filter(Log.id == id).one()

        if 'active' in doc.document:
            del doc.document['active']
            # @TODO: add robust saving mechanism
            try:
                self.session.begin()
                self.session.add(doc)
                self.session.commit()
            except:
                self.session.rollback()
                raise
