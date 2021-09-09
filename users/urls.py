from django.urls import path
from . import views
from .views import FormWizardView, FORMS

urlpatterns = [
    path('signup/', FormWizardView.as_view(FORMS), name='signup'),
    #path('login/', views.login_view, name='login'),
    #ath('logout/', views.logout_view, name='logout'),
]