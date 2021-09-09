from django.urls import path
from . import views


urlpatterns = [
    path('bulk_upload', views.upload, name='bulk_upload'),
]
