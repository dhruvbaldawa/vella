from flask.ext.testing import TestCase
from webapp.app import create_app, create_db, drop_db


class WebAppTestCase(TestCase):
    def setUp(self):
        super(WebAppTestCase, self).setUp()
        drop_db(self.app, True)
        create_db(self.app)

    def tearDown(self):
        drop_db(self.app, True)

    def create_app(self):
        return create_app('test')
