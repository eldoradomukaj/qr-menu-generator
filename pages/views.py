from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import path
from .forms import ContactForm

# Create your views here.


def home(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            from_email = form.cleaned_data['from_email']
            message = "Name: " + name + "\nemail: " + from_email + " \n \n" + form.cleaned_data['message']
            subject = "New contact form email from " + name + " (" + from_email + ") "
            try:
                send_mail(subject, message, 'contact@nomenu.io', ['contact@nomenu.io'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            form = ContactForm()
            messages.success(request, "Your message has been sent successfully.")

    context = { 
        'form': form,
        'dev_mode': True
    }
    return render(request, 'pages/index.html', context)

def send_contact_form(request):
    response_data = {}

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('from_email')
        message = request.POST.get('message')

        response_data['name'] = name
        response_data['email'] = email
        response_data['message'] = message

        if response_data:
            message = "Name: " + response_data['name'] + "\nemail: " + response_data['email'] + " \n \n" + response_data['message']
            subject = "New contact form email from " + response_data['name'] + " (" + response_data['email'] + ") "

            try:
                send_mail(subject, message, 'contact@nomenu.io', ['contact@nomenu.io'])
            except BadHeaderError:
                return HttpResponse("Invalid header!")
        return JsonResponse(response_data)

def privacy_policy_view(request):
    return render(request, 'pages/privacy_policy.html', context={})

def terms_view(request):
    return render(request, 'pages/terms.html', context={})

def handler404(request, *args, **kwargs):
    return render(request, '404.html', status=404)

def handler500(request, *args, **kwargs):
    return render(request, '500.html', status=500)