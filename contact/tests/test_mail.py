from django.core import mail
from django.test import TestCase
from django.urls import reverse

from django.conf import settings

class MailTests(TestCase):
    def setUp(self):
        url = reverse('contact:contact')
        data = {
            'email': 'john@doe.com',
            'subject': 'abcdef123456',
            'message': 'abcdef123456'
        }
        self.response = self.client.post(url, data)
        self.email = mail.outbox[0]
    
    def test_email_exists(self):
        '''
        Inbox is not empty
        '''
        self.assertEqual(len(mail.outbox), 1)

    def test_email_subject(self):
        '''
        Successful Subject Line
        '''
        self.assertEqual('abcdef123456', self.email.subject)

    def test_email_message(self):
        '''
        Successful Message
        '''
        self.assertIn('abcdef123456', self.email.body)
        self.assertIn('john@doe.com', self.email.body)

    def test_email_reciever(self):
        '''
        Successful Recipient Address
        '''
        self.assertEqual([settings.RECIPIENT_ADDRESS], self.email.to)