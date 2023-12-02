from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

import bleach
import os

from .models import *

class DownloadResultForm(forms.ModelForm):
    # Insert Reference Code and then Download Results
    class Meta:
        model = download_result
        fields = ('reference_code',)
        widgets = {
                'reference_code': forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : "e.g complex_6K9SDfw"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reference_code'].help_text = 'Please insert the reference code we have sent you via mail.'
        self.helper = FormHelper()
        self.helper.use_custom_control = False
        self.helper.layout = Layout(
            'reference_code',
            Submit('submit', 'Download', css_class='btn btn-primary btn-block')
        )
    
    def clean_data(self):
        reference_code = str(bleach.clean(self.cleaned_data["reference_code"]).replace(" ",""))
        return reference_code