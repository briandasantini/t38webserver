from django.test import TestCase

from ..forms import *

class cPEPFormTest(TestCase):
    def test_form_has_fields(self):
        '''
        Are all Needed Form Field Present?
        '''
        form = cPEPForm()
        expected = ['pdb', 'peptide_name', 'protein_chain_name', 'receptor_chain_name', 'cutoff', 'treshold', 'motif', 'email']
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)