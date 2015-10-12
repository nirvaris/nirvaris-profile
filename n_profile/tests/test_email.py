from django.core import mail
from django.test import TestCase, RequestFactory

from .commons import create_user_jack
from ..email import *

class EmailTestCase(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()

    def tearDown(self):
        ...

    def test_send_new_password(self):
        
        mail.outbox = []
        
        jack_user = create_user_jack()
        request = self.factory.get('/')
        
        send_new_password(request, jack_user, 'new_password')
        
        self.assertEqual(len(mail.outbox), 1,'It should sent an email')
    
    def test_send_activation_email(self):
        
        mail.outbox = []
    
        jack_user = create_user_jack()
        request = self.factory.get('/')
    
        send_activation_email(request, jack_user)
    
        self.assertEqual(len(mail.outbox), 1,'It should sent an email')
