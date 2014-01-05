from utils import WebAppTestCase


class ApiTestCase(WebAppTestCase):
    def setUp(self):
        super(ApiTestCase, self).setUp()
        from webapp.api import register
        register('Test User', 'test', 'test')

    def _login(self, username, password):
        return self.client.post('/api/v1/login',
                                data={'username': username,
                                      'password': password})

    def test_user_login(self):
        ''' test valid login. '''
        r = self._login('test', 'test')
        self.assert_200(r)

    def test_invalid_login(self):
        ''' test invalid login. '''
        r = self._login('test', 'test_password')
        self.assert_401(r)
