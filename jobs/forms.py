import bleach
import os
import shutil
import time
import glob

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.forms.widgets import Widget
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.conf import settings
from django.core.mail import EmailMessage
from django.template import loader
from .models import *
from .utils import exec_script




'''
Each Class belongs to one certain Script.
The Structure is always the same:
|-| Decide on the Form Layout
|-| Clean the recieved Data
|-| Start The respective Script
|-| Send The Results via Mail
|-| Delete Older Results Folder in Media/

'''    
############################################################## RS REMD SCRIPT ##############################################################

class RSREMDForm(forms.ModelForm):
    
    class Meta:
        model = rsremd
        fields = ('pdb', 'protein_complex_name', 'receptor_chain_end', 'ligand_chain_end', 'email')
        widgets = {
                'pdb': forms.FileInput(),
                'protein_complex_name': forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : "1AY7 complex"}),
                'receptor_chain_end': forms.NumberInput(attrs={'class' : 'form-control', 'placeholder' : "89"}),
                'ligand_chain_end': forms.NumberInput(attrs={'class' : 'form-control', 'placeholder' : "185"}),
                'email': forms.EmailInput(attrs={'class' : 'form-control', 'placeholder':"maxmustermann@email.de"}),
                
        }
        labels = {
            'pdb': 'PDB File'
        }

    def __init__(self, *args, **kwargs):
        # Plan Layout
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.use_custom_control = False
        self.helper.layout = Layout(
            'pdb',
            'protein_complex_name',
            Row(
                Column('receptor_chain_end', css_class='form-group col-md-6 mb-0'),
                Column('ligand_chain_end', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'email',
            Submit('submit', 'Submit', css_class='btn btn-primary btn-block')
        )

    def clean_rsremd_data(self):
        # Clean Submitted Data
        pdb = self.cleaned_data["pdb"]
        receptor_chain = self.cleaned_data["receptor_chain_end"]
        ligand_chain = self.cleaned_data["ligand_chain_end"]
        reference_name1 = bleach.clean(self.cleaned_data["protein_complex_name"])
        email1 = bleach.clean(self.cleaned_data["email"])

        # If there are any spaces, it will conflict with the command line later on. So strip them from the Text Inputs.
        protein_file_name = pdb.name.replace('.pdb', '')
        reference_name = reference_name1.replace(" ","-") 
        email = email1.strip()

        return protein_file_name, receptor_chain, ligand_chain, reference_name, email

############################################################## CPEP SCRIPT ##############################################################

class cPEPForm(forms.ModelForm):
   
    # Additional field for hot-spots targeting
    target_hotspots = forms.BooleanField(required=False, label="  I want to target specific hot-spots.")
    residue_numbers = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 
        'placeholder': '356 357 359 360 362 363', 
        'style': 'display: none;',  # Initially hidden
    }))
    class Meta:
        model = cpep
        fields = ('pdb', 'peptide_name', 'protein_chain_name', 'receptor_chain_name', 
                  'cutoff', 'treshold', 'motif', 'email', 'target_hotspots', 'residue_numbers')
        widgets = {
                'pdb': forms.FileInput(),
                'peptide_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "system"}),
                'protein_chain_name': forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : "A"}),
                'receptor_chain_name': forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : "B"}),
                'cutoff': forms.NumberInput(attrs={'class' : 'form-control', 'placeholder' : "6.0"}),
                'treshold': forms.NumberInput(attrs={'class' : 'form-control', 'placeholder' : "0.7"}),
                'motif': forms.NumberInput(attrs={'class' : 'form-control', 'placeholder' : "5"}),
                'email': forms.EmailInput(attrs={'class' : 'form-control', 'placeholder':"maxmustermann@email.de"}),
        }
        labels = {
            'peptide_name': 'Job Name',
            'protein_chain_name': 'Protein Chain',
            'receptor_chain_name': 'Receptor Chain',
            'pdb': 'PDB File',
            'residue_numbers': 'Hotspot Residue Numbers',
        }

    def __init__(self, *args, **kwargs):
        # Plan Layout
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.use_custom_control = False
        self.helper.layout = Layout(
            'peptide_name',
            'pdb',
            Row(
                Column('protein_chain_name', css_class='form-group col-md-6 mb-0'),
                Column('receptor_chain_name', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('cutoff', css_class='form-group col-md-6 mb-0'),
                Column('treshold', css_class='form-group col-md-4 mb-0'),
                Column('motif', css_class='form-group col-md-2 mb-0'),
                css_class='form-row'
            ),
            'target_hotspots',
            'residue_numbers',
            'email',
            Submit('submit', 'Submit', css_class='btn btn-primary btn-block')
        )

    def clean_data(self):
        # Clean Submitted Data
        peptide_pdb = self.cleaned_data["pdb"]
        protein_chain_name1 = bleach.clean(self.cleaned_data["protein_chain_name"])
        receptor_chain_name1 = bleach.clean(self.cleaned_data["receptor_chain_name"])
        cutoff = self.cleaned_data["cutoff"]
        treshold = self.cleaned_data["treshold"]
        motif = self.cleaned_data["motif"]
        reference_name1 = bleach.clean(self.cleaned_data["peptide_name"])
        email1 = bleach.clean(self.cleaned_data["email"])

        # If there are any spaces, it will conflict with the command line later on. So strip them from the Text Inputs.
        protein_chain_name = protein_chain_name1.strip()
        receptor_chain_name = receptor_chain_name1.strip()
        protein_file_name = peptide_pdb.name.replace('.pdb', '')
        reference_name = reference_name1.replace(" ","-")
        email = email1.strip()
        
        # Check if specific residues are provided
        target_hotspots = self.cleaned_data.get("target_hotspots")
        residue_numbers = self.cleaned_data.get("residue_numbers").strip()
        
        
        return protein_file_name, protein_chain_name, receptor_chain_name, cutoff, treshold, motif, reference_name, email, target_hotspots, residue_numbers

    