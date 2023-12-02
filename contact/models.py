from django.db import models


class contact(models.Model):
    email = models.EmailField(blank=False)
    subject = models.CharField(max_length=70, blank=False)
    message = models.CharField(blank=False, max_length=3000, help_text='The max length of the text is 3000.')
