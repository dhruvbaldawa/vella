import time
from unittest import TestCase
from vella.backends.mongo import MongoLogger
from pymongo import MongoClient


class MongoLoggerTest(TestCase):
    def setUp(self):
        self.db_name = 'test_db'
        self.client = MongoClient()
        self.db = self.client[self.db_name]['logs']  # ALERT!
        self.logger = MongoLogger('mongodb://localhost:27017/' + self.db_name)

    def log(self, *args, **kwargs):
        doc_id = self.logger.log(*args, **kwargs)
        db_doc = self.db.find_one(doc_id)
        self.assertEqual(db_doc['_id'], doc_id)
        return db_doc

    def log_event(self, doc_id, event, **kwargs):
        self.logger.log_event(doc_id, event, **kwargs)
        db_doc = self.db.find_one(doc_id)
        return db_doc

    def test_log(self):
        ''' test if the document is being created or not. '''
        self.log('test', 'unit_test')

    def test_log_timestamp(self):
        ''' test if the document is being created with the supplied
        timestamp or not. '''
        current_time = time.time()
        db_doc = self.log('test', 'unit_test', timestamp=current_time)
        self.assertEqual(db_doc['timestamp'], current_time)

    def test_log_other_fields(self):
        ''' test if the other fields are being properly populated or not. '''
        doc = {
            'kind': 'test',
            'source': 'unit_test',
            'description': 'some description',
            'arg1': 'value1',
            'arg2': 'value2',
        }
        db_doc = self.log(**doc)
        for key in doc:
            self.assertEqual(db_doc[key], doc[key])

    def test_event(self):
        ''' test adding a simple event. '''
        db_doc = self.log('test', 'unit_test')
        db_doc = self.log_event(db_doc['_id'], 'test_event')

        self.assertIn('timeline', db_doc)
        self.assertEqual(db_doc['timeline'][0]['event'], 'test_event')

    def test_multiple_events(self):
        ''' test adding multiple events. '''
        db_doc = self.log('test', 'unit_test')
        db_doc = self.log_event(db_doc['_id'], 'test_event')
        db_doc = self.log_event(db_doc['_id'], 'test_event2')

        self.assertEqual(db_doc['timeline'][0]['event'], 'test_event')
        self.assertEqual(db_doc['timeline'][1]['event'], 'test_event2')

    def test_event_timestamp(self):
        ''' test for events with supplied timestamps. '''
        db_doc = self.log('test', 'unit_test')
        current_time = time.time()
        db_doc = self.log_event(db_doc['_id'], 'test_event',
                                timestamp=current_time)

        self.assertEqual(db_doc['timeline'][0]['timestamp'], current_time)

    def test_event_chronological(self):
        ''' test for events with supplied timestamps are in chronological
        order or not. '''
        db_doc = self.log('test', 'unit_test')
        earlier = time.time()
        later = time.time() + 4

        self.log_event(db_doc['_id'], 'next_event', timestamp=later)
        db_doc = self.log_event(db_doc['_id'], 'test_event', timestamp=earlier)

        self.assertEqual(db_doc['timeline'][0]['event'], 'test_event')
        self.assertEqual(db_doc['timeline'][1]['event'], 'next_event')

    def test_event_inactive(self):
        ''' test active flag for an inactive event. '''
        db_doc = self.log('test', 'unit_test')
        db_doc = self.log_event(db_doc['_id'], 'test_event', active=False)

        self.assertNotIn('active', db_doc)

    def test_event_active(self):
        ''' test active flag for an active event. '''
        db_doc = self.log('test', 'unit_test')
        db_doc = self.log_event(db_doc['_id'], 'test_event')

        self.assertTrue(db_doc['active'])

    def tearDown(self):
        self.client.drop_database(self.db_name)
