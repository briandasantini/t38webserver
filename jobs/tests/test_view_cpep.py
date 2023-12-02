import os
import shutil

from django.test import TestCase, override_settings
from django.urls import resolve, reverse
from unittest import skip

from ..forms import cPEPForm
from ..views import cPEPView

'''

To Do List
|-| write function to test if cpep script was connected successfully
|-| write function to test if cpep script ran error free
|-| write function to test if result email was send successfully
|-| write function to test if error email was send successfully

'''

class cPEPViewTests(TestCase):
    def setUp(self):
        url = reverse('job:cpep')
        self.response = self.client.get(url)

    def test_cpep_status_code(self):
        '''
        URL exists at correct location
        '''
        self.assertEquals(self.response.status_code, 200)

    def test_cpep_url_resolves_cpep_view(self):
        '''
        Successfully resolves cPEP View from URL
        '''
        view = resolve('/cpep/')
        self.assertEquals(view.func.__name__, cPEPView.as_view().__name__)

    def test_template_name_correct(self):
        '''
        URL shows right HTML Template
        '''
        self.assertTemplateUsed(self.response, "cpep.html")

    def test_contains_form(self):
        '''
        cPEP View contains cPEPForm
        '''
        form = self.response.context.get('form')
        self.assertIsInstance(form, cPEPForm)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_form_inputs(self):
        '''
        cPEPForm must contain six inputs: csrf (submit button), pdb, peptide_name, protein_chain_name, receptor_chain_name, cutoff, treshold, motif, email
        '''
        print()
        self.assertContains(self.response, '<input', 10)
        self.assertContains(self.response, 'type="file"', 1)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="number"', 3)
        self.assertContains(self.response, 'type="text"', 3)
        self.assertContains(self.response, 'type="submit"',1)
        self.assertContains(self.response, 'type="button"',1)

class SuccessfulcPEPSubmitTests(TestCase):
        def setUp(self):
            '''
            Setting Up TestCase
            '''
            url = reverse('job:cpep')
            file_path = os.path.join(os.path.dirname(__file__), '../../scripts/cpep/sample/complex.pdb')
            sample_pdb = open(file_path)
            data = {
                'pdb': sample_pdb,
                'peptide_name': 'Complex', 
                'protein_chain_name': 'E', 
                'receptor_chain_name': 'A', 
                'cutoff': '7.0', 
                'treshold': '0.7', 
                'motif': '4',
                'email': 'yasmin.saremi@gmail.com',
            }
            self.response = self.client.post(url, data)
            self.home_url = reverse('home')
            self.home_response = self.client.get(self.home_url)
        
        @skip("Don't want to test")
        def test_redirection(self):
            '''
            A valid form submission should redirect the user to the home page and show the success message there
            '''
            self.assertRedirects(self.response, self.home_url)
            messages = list(self.home_response.context.get('messages'))
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), cPEPView.success_message)

class InvalidcPEPSubmitTests(TestCase):
    def setUp(self):
        url = reverse('job:cpep')
        self.response = self.client.post(url, {})  # submit an empty dictionary

    def test_cpep_status_code(self):
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