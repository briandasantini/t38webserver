import os
import shutil

from django.test import TestCase, override_settings
from django.urls import resolve, reverse
from unittest import skip

from ..forms import RSREMDForm
from ..views import RSREMDView

'''

To Do List
|-| write function to test if rsremd script was connected successfully
|-| write function to test if rsremd script ran error free
|-| write function to test if result email was send successfully
|-| write function to test if error email was send successfully

'''

class RSREMDViewTests(TestCase):
    def setUp(self):
        url = reverse('job:rsremd')
        self.response = self.client.get(url)

    def test_rsremd_status_code(self):
        '''
        URL exists at correct location
        '''
        self.assertEquals(self.response.status_code, 200)

    def test_rsremd_url_resolves_rsremd_view(self):
        '''
        Successfully resolves RSREMD View from URL
        '''
        view = resolve('/rsremd/')
        self.assertEquals(view.func.__name__, RSREMDView.as_view().__name__)

    def test_template_name_correct(self):
        '''
        URL shows right HTML Template
        '''
        self.assertTemplateUsed(self.response, "rsremd.html")

    def test_contains_form(self):
        '''
        RSREMD View contains RSREMDForm
        '''
        form = self.response.context.get('form')
        self.assertIsInstance(form, RSREMDForm)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_form_inputs(self):
        '''
        RSREMDForm must contain six inputs: csrf (submit button), pdb, protein_complex_name, receptor_chain_end, ligand_chain_end, email
        '''
        print()
        self.assertContains(self.response, '<input', 7)
        self.assertContains(self.response, 'type="file"', 1)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="number"', 2)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="submit"',1)
        self.assertContains(self.response, 'type="button"',1)

class SuccessfulRSREMDSubmitTests(TestCase):
    def setUp(self):
        '''
        Setting Up TestCase
        '''
        url = reverse('job:rsremd')
        file_path = os.path.join(os.path.dirname(__file__), '../../scripts/rsremd/sample.pdb')
        sample_pdb = open(file_path)
        data = {
            'pdb': sample_pdb,
            'protein_complex_name': '1AY7 complex',
            'receptor_chain_end': '89',
            'ligand_chain_end': '185',
            'email': 'john@doe.com',
        }
        self.response = self.client.post(url, data)
        self.home_url = reverse('home')
        self.home_response = self.client.get(self.home_url)

    @skip("Don't want to test")
    def test_redirection(self):
        '''
        A valid form submission should redirect the user to the home page and show the success message there
        Needs to be done yet
        '''
        self.assertRedirects(self.response, self.home_url)
        messages = list(self.home_response.context.get('messages'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), RSREMDView.success_message)

class InvalidRSREMDSubmitTests(TestCase):
    def setUp(self):
        url = reverse('job:rsremd')
        self.response = self.client.post(url, {})  # submit an empty dictionary

    def test_rsremd_status_code(self):
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