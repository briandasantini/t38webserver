from django.views.generic import TemplateView, FormView
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.conf import settings

import mimetypes
import os
import zipfile
import glob
from io import BytesIO

from .forms import *

class HomePageView(TemplateView):
    template_name = 'home.html'

class TutorialPageView(TemplateView):
    template_name = "help.html"

class ResultPageView(FormView):
    template_name = "result_page.html"
    model = download_result
    form_class = DownloadResultForm
    success_url = reverse_lazy('home')
    success_message = "Download was successfully"
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

def download_file(request):
    '''
    used code from 
    https://fedingo.com/how-to-download-file-in-django/
    https://stackoverflow.com/questions/70458166/django-how-to-pass-html-form-values-to-url-upon-form-submission
    https://stackoverflow.com/questions/19459300/how-to-serve-downloadable-zip-file-in-django
    '''
    # Define Django project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Define text file name
    req = request.GET.get('reference_code', None)
    filename = req.strip()

    # Define the full file path
    filepath = BASE_DIR + '/media/' + str(filename)
    if os.path.exists(filepath)==True:
        # Files (local path) to put in the .zip
        filename_list = glob.glob('./media/'+filename+'/*')
        # Folder name in ZIP archive which contains the above files
        # E.g [thearchive.zip]/somefiles/file2.txt
        zip_subdir = "results"
        zip_filename = "zacharias-web_results.zip"
        # Open StringIO to grab in-memory ZIP contents
        s = BytesIO()
        # The zip compressor
        zf = zipfile.ZipFile(s, "w")
        for fpath in filename_list:
            # Calculate path for file in zip
            fdir, fname = os.path.split(fpath)
            zip_path = os.path.join(zip_subdir, fname)
            # Add file, at correct path
            zf.write(fpath, zip_path)
        # Must close zip for all contents to be written
        zf.close()
        # Grab ZIP file from in-memory, make response with correct MIME-type
        response = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
        # ..and correct content-disposition
        response['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return response
    else:
        # Load the template
        messages.warning(request, 'Your Reference Code is invalid - Please Check Again.')
        # return render(request, 'result_page.html')
        return redirect('result_page')