from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from syscor.views.auth import UserRegistration


class UserRegistrationTests(SimpleTestCase):
    def test_post_returns_response_for_every_registration_step(self):
        cases = [
            ({}, False, 'userregistration', 'step01'),
            ({'registration_step': ''}, False, 'userregistration', 'step01'),
            ({'registration_step': 'unknown'}, False, 'userregistration', 'step01'),
            ({'registration_step': 'step01'}, False, 'userregistration', 'step02'),
            ({'registration_step': 'step02'}, False, 'userprofile', None),
            ({}, True, 'userprofile', None),
        ]
        for data, authenticated, module, next_step in cases:
            with self.subTest(data=data, authenticated=authenticated):
                request = RequestFactory().post('/registration', data)
                request.user = SimpleNamespace(is_authenticated=authenticated)
                response = HttpResponse('OK')
                with (
                    patch('syscor.views.auth.WebMachine.web_renderer', return_value=response) as renderer,
                    patch('syscor.views.auth.SysLogging.log'),
                ):
                    result = UserRegistration.as_view()(request)
                self.assertIs(result, response)
                self.assertEqual(renderer.call_args.args[2], module)
                self.assertEqual(renderer.call_args.args[3].get('registration_step'), next_step)
