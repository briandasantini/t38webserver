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

class ContactForm(forms.ModelForm):
    class Meta:
        model = contact
        fields = ('email', 'subject', 'message')
        widgets = {
            'email': forms.EmailInput(attrs={'class' : 'form-control', 'placeholder':"maxmustermann@email.de"}),
            'subject': forms.TextInput(attrs={'class' : 'form-control', 'placeholder' : "Your Subject"}),
            'message': forms.Textarea(attrs={'class' : 'form-control', 'placeholder' : "How can we help you?", 'rows':9})
                    
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.use_custom_control = False
        self.helper.layout = Layout(
            'email',
            'subject',
            'message',
            Submit('submit', 'Submit', css_class='btn btn-primary btn-block')
        )

    def get_info(self):
        """
        Method that returns formatted information
        :return: subject, msg
        """
        # Cleaned data
        cl_data = super().clean()

        from_email = cl_data.get('email')
        subject = cl_data.get('subject')

        msg = f'You recieved an invoice from the email adress {from_email}:'
        msg += f'\n"{subject}"\n\n'
        msg += cl_data.get('message')

        return subject, msg

    def send(self):

        subject, msg = self.get_info()
        mail = EmailMessage(subject, msg, settings.EMAIL_HOST_USER, [settings.RECIPIENT_ADDRESS])
        
        mail.send()