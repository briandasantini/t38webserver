import os
import shutil

from django.test import TestCase, override_settings
from django.urls import resolve, reverse
from unittest import skip

from ..forms import DownloadResultForm
from ..views import ResultPageView, download_file


class ResultPageViewTests(TestCase):
    def setUp(self):
        url = reverse('result_page')
        self.response = self.client.get(url)

    def test_result_page_status_code(self):
        '''
        URL exists at correct location
        '''
        self.assertEquals(self.response.status_code, 200)

    def test_result_page_url_resolves_result_page_view(self):
        '''
        Successfully resolves View from URL
        '''
        view = resolve('/results/')
        self.assertEquals(view.func.__name__, ResultPageView.as_view().__name__)

    def test_template_name_correct(self):
        '''
        URL shows right HTML Template
        '''
        self.assertTemplateUsed(self.response, "result_page.html")

    def test_contains_form(self):
        '''
        View contains Form
        '''
        form = self.response.context.get('form')
        self.assertIsInstance(form, DownloadResultForm)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_form_inputs(self):
        '''
        Form must contain two inputs: csrf (submit and button), reference_code
        '''
        print()
        self.assertContains(self.response, '<input', 3)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="submit"',1)
        self.assertContains(self.response, 'type="button"',1)

class SuccessfulDownloadTests(TestCase):
        def setUp(self):
            '''
            Setting Up TestCase
            '''
            url = reverse('download')
            data = {
                'reference_code':'complex',
            }
            self.response = self.client.get(url, data)
        
        def test_downlaod_file(self):
            '''
            A valid form submission download the file
            '''
            self.assertEquals(self.response.get('Content-Disposition'),"attachment; filename=complex.zip")

class InvalidResultsFormSubmitTests(TestCase):
    def setUp(self):
        url_form = reverse('result_page')
        self.response = self.client.post(url_form, {})  # submit an empty dictionary

        url_download = reverse('download')
        self.response_download = self.client.get(url_download, {})
        

    def test_result_page_status_code(self):
        '''
        An invalid form submission should return to the same page with an warning message
        '''
        self.assertEquals(self.response.status_code, 200)
        messages = list(self.client.post('/results/').context['messages'])
        self.assertEqual(len(messages), 1)

    def test_invalid_download(self):
            '''
            An invalid form submission should not download anything
            '''
            self.assertEquals(self.response_download.get('Content-Disposition'),None)