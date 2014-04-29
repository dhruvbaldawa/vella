import json
import uuid
import time
from utils import WebAppTestCase


class ApiTestCase(WebAppTestCase):
    def setUp(self):
        super(ApiTestCase, self).setUp()
        from webapp.api import register
        register('Test User', 'test', 'test')
        self._login('test', 'test')

    def _login(self, username, password):
        return self.client.post('/api/v1/login',
                                data={'username': username,
                                      'password': password})

    def _log(self, kind, source, timestamp=None, description=None, **other):
        data = {
            'kind': kind,
            'source': source,
            'timestamp': timestamp,
            'description': description,
            'other': json.dumps(other),
        }
        return self.client.post('/api/v1/log', data=data)

    def _get(self, doc_id):
        return self.client.get('/api/v1/log/{}'.format(doc_id))

    def _add_event(self, doc_id, event, timestamp=None, active=True, **other):
        data = {
            'event': event,
            'timestamp': timestamp,
            'active': active,
            'other': json.dumps(other),
        }
        return self.client.post('/api/v1/event/' + doc_id, data=data)

    def _deactivate(self, doc_id):
        return self.client.get('/api/v1/deactivate/{}'.format(doc_id))

    def test_invalid_login(self):
        ''' test invalid login. '''
        r = self._login('test', 'invalid_password')
        self.assert_401(r)

    def test_create_log(self):
        ''' test create log. '''
        r = self._log('test', 'unit_test')
        self.assert_200(r)

    def test_retrieve_log(self):
        ''' test retrieve log. '''
        data = {
            'kind': 'test',
            'source': 'unit_test',
        }

        r = self._log(**data)
        self.assert_200(r)
        r = self._get(r.json['doc_id'])
        self.assert_200(r)

        for k, v in data.iteritems():
            self.assertEquals(r.json[k], v)

    def test_retrieve_missing_log(self):
        ''' test retrieving a missing log. '''
        # @caution: assumes a uuid document id
        r = self._get(uuid.uuid4().hex)
        self.assert_404(r)

    def test_retrieve_log_all_fields(self):
        ''' test retrieve log with all fields.

        Secondary purpose of this test is to check the creation of logs
        with custom timestamps.
        '''
        data = {
            'kind': 'test',
            'source': 'unit_test',
            'timestamp': float(time.time()),
            'description': 'sample description',
            'foo': 'bar',
        }

        r = self._log(**data)
        self.assert_200(r)
        r = self._get(r.json['doc_id'])
        self.assert_200(r)

        for k, v in data.iteritems():
            # using assertAlmostEqual for timestamp checking
            # usual equality checking are also handled by assertAlmostEqual
            # after Python 2.7
            self.assertAlmostEqual(r.json[k], v, places=2)

    def test_add_event(self):
        ''' test adding an event. '''
        r = self._log('test', 'unit_test')
        r = self._add_event(r.json['doc_id'], 'test_event')
        self.assert_200(r)

    def test_add_event_missing_log(self):
        ''' test adding an event in a missing log. '''
        # @caution: assuming event id to always be an uuid
        r = self._add_event(uuid.uuid4().hex, 'test_event')
        self.assert_404(r)

    def test_add_event_inactive_log(self):
        ''' test adding an event to an inactive log.

        Currently, adding an event to an inactive log makes it active.
        '''
        r = self._log('test', 'unit_test')
        doc_id = r.json['doc_id']

        r = self._add_event(doc_id, 'test_event', active=False)
        self.assert_200(r)
        r = self._get(doc_id)
        self.assertNotIn('active', r.json)

        # try adding an event to the inactive log
        r = self._add_event(doc_id, 'test_event2')
        self.assert_200(r)
        r = self._get(doc_id)
        self.assertTrue(r.json['active'])

    def test_add_event_set_inactive(self):
        ''' test adding an event and making the log entry inactive. '''
        pass

    def test_add_event_custom_timestamp(self):
        ''' test adding event with custom timestamp. '''
        pass

    def test_deactivate_event(self):
        ''' test deactivating an event. '''
        r = self._log('test', 'unit_test')
        r = self._deactivate(r.json['doc_id'])
        self.assert_200(r)

    def test_deactive_inactive_event(self):
        ''' test deactivating an inactive event. '''
        pass

    def test_deactivate_missing_event(self):
        ''' test deactivating a missing event. '''
        # @caution: this assumes a uuid id for the document
        r = self._deactivate(uuid.uuid4().hex)
        self.assert_404(r)
