from django.test import TestCase
from django.urls import resolve, reverse

from ..forms import ContactForm
from ..views import ContactView

class ContactViewTests(TestCase):
    def setUp(self):
        url = reverse('contact:contact')
        self.response = self.client.get(url)

    def test_contact_status_code(self):
        '''
        URL exists at correct location
        '''
        self.assertEquals(self.response.status_code, 200)

    def test_contact_url_resolves_contact_view(self):
        '''
        Successfully resolves Contact View from Contact URL
        '''
        view = resolve('/contact/')
        self.assertEquals(view.func.__name__, ContactView.as_view().__name__)

    def test_template_name_correct(self):
        '''
        URL shows right HTML Template
        '''
        self.assertTemplateUsed(self.response, "contact.html")

    def test_contains_form(self):
        '''
        Contact View contains ContactForm
        '''
        form = self.response.context.get('form')
        self.assertIsInstance(form, ContactForm)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_form_inputs(self):
        '''
        ContactForm must contain four inputs: csrf (submit button), email, subject
        message is a textArea therefore has no input type - different check
        '''
        self.assertContains(self.response, '<input', 4)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="submit"',1)
        self.assertContains(self.response, 'type="button"',1)
        self.assertContains(self.response, '<textarea', 1)

class SuccessfulContactSubmitTests(TestCase):
    def setUp(self):
        url = reverse('contact:contact')
        data = {
            'email': 'john@doe.com',
            'subject': 'abcdef123456',
            'message': 'abcdef123456'
        }
        self.response = self.client.post(url, data)
        self.home_url = reverse('home')
        self.home_response = self.client.get(self.home_url)

    def test_redirection(self):
        '''
        A valid form submission should redirect the user to the home page
        '''
        self.assertRedirects(self.response, self.home_url)

    def test_redirection_succesmsg(self):
        '''
        A valid form submission should redirect the user to the home page and show the success message there
        Needs to be done yet
        '''
        messages = list(self.home_response.context.get('messages'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), ContactView.success_message)

class InvalidContactSubmitTests(TestCase):
    def setUp(self):
        url = reverse('contact:contact')
        self.response = self.client.post(url, {})  # submit an empty dictionary

    def test_contact_status_code(self):
        '''
        An invalid form submission should return to the same page
        '''
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        '''
        An invalid form submission should return the same form with error messages
        '''
        form = self.response.context.get('form')
        self.assertTrue(form.errors)