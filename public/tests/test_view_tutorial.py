from django.test import TestCase
from django.urls import resolve, reverse

from ..views import *

class TutorialViewTests(TestCase):
    def setUp(self):
        url = reverse('help')
        self.response = self.client.get(url)

    def test_home_status_code(self):
        '''
        URL exists at correct location
        '''
        self.assertEquals(self.response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        '''
        Successfully resolves Tutorial View from URL
        '''
        view = resolve('/help/')
        self.assertEquals(view.func.__name__, TutorialPageView.as_view().__name__)

    def test_template_name_correct(self):
        '''
        URL shows right HTML Template
        '''
        self.assertTemplateUsed(self.response, "help.html")