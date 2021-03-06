import mock
import time
from unittest import TestCase
from vella.logger import DatabaseError, InvalidDatabaseURL
from vella.backends.postgresql import Log, PostgresqlLogger, Base


class LoggerTestCase(TestCase):
    db_name = 'test_db'
    __test__ = False
    logger = None

    def get_document(self, id):
        pass  # pragma: no cover

    def log(self, *args, **kwargs):
        id = self.logger.log(*args, **kwargs)
        db_doc = self.get_document(id)
        self.assertEqual(db_doc['id'], id)
        return db_doc

    def log_event(self, id, event, **kwargs):
        self.logger.log_event(id, event, **kwargs)
        db_doc = self.get_document(id)
        return db_doc

    def test_log(self):
        ''' test if the document is being created or not. '''
        self.log('test', 'unit_test')

    def test_log_timestamp(self):
        ''' test if the document is being created with the supplied
        timestamp or not. '''
        current_time = time.time()
        time.sleep(1)
        db_doc = self.log('test', 'unit_test', timestamp=current_time)
        self.assertAlmostEquals(db_doc['timestamp'], current_time, places=2)

    def test_log_other_fields(self):
        ''' test if the other fields are being properly populated or not. '''
        doc = {
            'kind': 'test',
            'source': 'unit_test',
            'arg1': 'value1',
            'arg2': 'value2',
        }
        db_doc = self.log(**doc)
        for key in doc:
            self.assertEqual(db_doc[key], doc[key])

    def test_event(self):
        ''' test adding a simple event. '''
        db_doc = self.log('test', 'unit_test')
        db_doc = self.log_event(db_doc['id'], 'test_event')

        self.assertIn('timeline', db_doc)
        self.assertEqual(db_doc['timeline'][0]['event'], 'test_event')

    def test_multiple_events(self):
        ''' test adding multiple events. '''
        db_doc = self.log('test', 'unit_test')
        db_doc = self.log_event(db_doc['id'], 'test_event')
        db_doc = self.log_event(db_doc['id'], 'test_event2')

        self.assertEqual(db_doc['timeline'][0]['event'], 'test_event')
        self.assertEqual(db_doc['timeline'][1]['event'], 'test_event2')

    def test_event_timestamp(self):
        ''' test for events with supplied timestamps. '''
        db_doc = self.log('test', 'unit_test')
        current_time = time.time()
        db_doc = self.log_event(db_doc['id'], 'test_event',
                                timestamp=current_time)

        self.assertEqual(db_doc['timeline'][0]['timestamp'], current_time)

    def test_event_chronological(self):
        ''' test for events with supplied timestamps are in chronological
        order or not. '''
        db_doc = self.log('test', 'unit_test')
        earlier = time.time()
        later = time.time() + 4

        self.log_event(db_doc['id'], 'next_event', timestamp=later)
        db_doc = self.log_event(db_doc['id'], 'test_event', timestamp=earlier)

        self.assertEqual(db_doc['timeline'][0]['event'], 'test_event')
        self.assertEqual(db_doc['timeline'][1]['event'], 'next_event')

    def test_event_inactive(self):
        ''' test active flag for an inactive event. '''
        db_doc = self.log('test', 'unit_test')
        db_doc = self.log_event(db_doc['id'], 'test_event', active=False)

        self.assertNotIn('active', db_doc)

    def test_event_active(self):
        ''' test active flag for an active event. '''
        db_doc = self.log('test', 'unit_test')
        db_doc = self.log_event(db_doc['id'], 'test_event')

        self.assertTrue(db_doc['active'])

    def test_user_given_id(self):
        given_id = 'new_log_123'
        db_doc = self.log('test', id=given_id)
        system_id = db_doc['id']
        self.assertEqual(self.get_document(given_id),
                         self.get_document(system_id))

    def test_user_given_id_update(self):
        # test if the user given id updates the correct log
        pass


class PostgresqlLoggerTestCase(LoggerTestCase):
    __test__ = True

    def setUp(self):
        self.logger = PostgresqlLogger('postgresql://test:test@localhost/test_db')
        Base.metadata.create_all(self.logger._engine)

    def get_document(self, id):
        return self.logger.get(id)

    def test_set_document_fields(self):
        data = {
            'kind': 'test',
            'timestamp': int(time.time()),
            'source': 'source',
        }
        db_doc = self.log(id='unit_test', **data)
        db_obj = self.logger._get(db_doc['id'])

        for k, v in data.iteritems():
            self.assertEqual(getattr(db_obj, k), v)

    def tearDown(self):
        Base.metadata.drop_all(self.logger._engine)


class PostgresqlDatabaseTestCase(TestCase):
    def create_logger(self, url='postgresql://test:test@localhost/test_db'):
        logger = PostgresqlLogger(url)
        logger._verify_database()

    def test_postgresql_database_url(self):
        with self.assertRaises(InvalidDatabaseURL):
            self.create_logger('notpostgres://foo:bar@localhost/db')

    @mock.patch('sqlalchemy.dialects.postgresql.base.'
                'PGDialect._get_server_version_info',
                lambda x, y: (9, 3, 0))
    def test_invalid_postgresql_version(self):
        with self.assertRaises(DatabaseError):
            self.create_logger()

    @mock.patch('sqlalchemy.dialects.postgresql.base.'
                'PGDialect._get_server_version_info',
                lambda x, y: (8, 3, 0))
    def test_invalid_postgresql_version_8(self):
        with self.assertRaises(DatabaseError):
            self.create_logger()

    @mock.patch('sqlalchemy.dialects.postgresql.base.'
                'PGDialect._get_server_version_info',
                lambda x, y: (9, 5, 0))
    def test_valid_postgresql_version(self):
        self.create_logger()

    @mock.patch('sqlalchemy.dialects.postgresql.base.'
                'PGDialect._get_server_version_info',
                lambda x, y: (9, 4, 0))
    def test_postgresql_9_4(self):
        self.create_logger()
