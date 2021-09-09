from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='index'),
    path('sendcontact/', views.send_contact_form, name='send-contact-form'),
    path('privacypolicy/', views.privacy_policy_view, name='privacy-policy'),
    path('terms/', views.terms_view, name='terms')
]