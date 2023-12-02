from django.test import TestCase

from ..forms import *

class RSREMDFormTest(TestCase):
    def test_form_has_fields(self):
        '''
        Are all Needed Form Field Present?
        '''
        form = RSREMDForm()
        expected = ['pdb', 'protein_complex_name', 'receptor_chain_end', 'ligand_chain_end', 'email']
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)