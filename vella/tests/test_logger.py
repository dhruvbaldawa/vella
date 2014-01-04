from unittest import TestCase
from vella.logger import Logger
from pymongo import MongoClient


class LoggerTest(TestCase):
    def setUp(self):
        self.db_name = 'test_db'
        self.client = MongoClient()
        self.db = self.client[self.db_name]['logs']  # ALERT!
        self.logger = Logger(db=self.db_name)

    def test_log(self):
        ''' test if the document is being created or not. '''
        doc_id = self.logger.log('test', 'unit_test')
        self.assertEqual(self.db.find_one(doc_id)['_id'], doc_id)

    def tearDown(self):
        self.client.drop_database(self.db_name)
