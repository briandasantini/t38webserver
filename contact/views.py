from django.shortcuts import render
from django.views.generic import FormView
from .forms import ContactForm
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

class ContactView(SuccessMessageMixin, FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('home')
    success_message = "We recieved your message and will get back to you soon!"
    def form_valid(self, form):
        # Calls the custom send method
        form.send()
        return super().form_valid(form)