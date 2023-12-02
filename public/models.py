from django.db import models

class download_result(models.Model):
    reference_code = models.CharField(max_length=100, blank=False, verbose_name="")