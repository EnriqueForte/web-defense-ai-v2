"""Offline transport regression for shared Secure cookies (GHSA-494j-54xm-rwp3)."""
from asyncio import AbstractEventLoop
from http.cookies import SimpleCookie
from importlib.util import find_spec
from unittest import TestCase, skipUnless
from unittest.mock import Mock, patch


@skipUnless(find_spec('aiohttp'), 'Full transport environment required')
class SharedCookieSecurityTests(TestCase):
    def test_secure_shared_cookie_stays_off_cleartext_after_cache_warmup(self):
        from aiohttp import CookieJar
        from yarl import URL

        # Cookie filtering never schedules work; avoid creating an event loop/socket.
        jar = CookieJar(loop=Mock(spec=AbstractEventLoop))
        cookies = SimpleCookie()
        cookies['session'] = 'synthetic-session'
        cookies['session']['secure'] = True
        cookies['preference'] = 'synthetic-preference'
        jar.update_cookies(cookies)
        with patch('socket.socket.connect', side_effect=AssertionError('Network forbidden')):
            for scheme in ('https', 'http', 'wss', 'ws', 'https', 'http'):
                with self.subTest(scheme=scheme):
                    selected = jar.filter_cookies(URL(f'{scheme}://lab.invalid/'))
                    self.assertIn('preference', selected)
                    self.assertEqual('session' in selected, scheme in ('https', 'wss'))

    def test_secure_origin_exception_is_limited_to_explicit_origin(self):
        from aiohttp import CookieJar
        from yarl import URL

        trusted = URL('http://lab.invalid:8080/')
        jar = CookieJar(treat_as_secure_origin=[trusted], loop=Mock(spec=AbstractEventLoop))
        cookies = SimpleCookie()
        cookies['session'] = 'synthetic-session'
        cookies['session']['secure'] = True
        jar.update_cookies(cookies)
        with patch('socket.socket.connect', side_effect=AssertionError('Network forbidden')):
            self.assertIn('session', jar.filter_cookies(trusted))
            for target in ('http://lab.invalid:8081/', 'http://other.invalid:8080/'):
                with self.subTest(target=target):
                    self.assertNotIn('session', jar.filter_cookies(URL(target)))
