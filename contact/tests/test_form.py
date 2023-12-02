from django.test import TestCase

from ..forms import ContactForm

class ContactFormTest(TestCase):
    def test_form_has_fields(self):
        form = ContactForm()
        expected = ['email', 'subject', 'message']
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)