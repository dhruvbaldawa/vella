import json
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
        r = self._log('test', 'unit_test')
        self.assert_200(r)
        r = self._get(r.json['doc_id'])
        self.assert_200(r)

        self.assertEqual(r.json['kind'], 'test')
        self.assertEqual(r.json['source'], 'unit_test')

    def test_retrieve_missing_log(self):
        ''' test retrieving a missing log. '''
        r = self._get('13ec70d530444d729a1417d33d03e1da')
        self.assert_404(r)

    def test_retrieve_log_all_fields(self):
        ''' test retrieve log with all fields. '''
        pass
