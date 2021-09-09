from django import forms
from django.forms import ModelForm
from allauth.account.forms import SignupForm, LoginForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from restaurant.models import Restaurant
from localflavor.us.forms import USStateSelect, USZipCodeField, USStateField


class UserCreateForm(SignupForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone_number = forms.CharField(required=True, max_length=12)
    signup_code = forms.CharField(required=True, max_length=10)
    
    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name'})
        self.fields['email'].widget.attrs.update({'placeholder': 'E-Mail'})
        self.fields['phone_number'].widget.attrs.update({'placeholder': 'Phone Number'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})
        self.fields['signup_code'].widget.attrs.update({'placeholder': 'Sign Up Code'})

        self.fields['first_name'].error_messages = {'required': 'Please enter your first name.'}
        self.fields['last_name'].error_messages = {'required': 'Please enter your last name.'}
        self.fields['phone_number'].error_messages = {'required': 'Please enter your phone number.'}
        self.fields['email'].error_messages = {'required': 'A valid email is required.'}
        self.fields['password1'].error_messages = {'required': 'Please enter a password.'}
        self.fields['password2'].error_messages = {'required': 'Please confirm your password.'}
        self.fields['signup_code'].error_messages = {'required': 'Please enter your sign up code.'}

        for fieldname in ['first_name','last_name', 'email', 'phone_number', 'password1', 'password2', 'signup_code']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].label = ''

    def save(self, request):
        user = super(UserCreateForm, self).save(request)

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.save()

        return user

class LoginUserForm(LoginForm):
    password = forms.PasswordInput()
    login = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(LoginUserForm, self).__init__(*args, **kwargs)
        self.fields['password'].label = ''
        self.fields['login'].label = ''
        self.fields['login'].error_messages = {'required': 'Please enter your e-mail address.'}
        self.fields['password'].error_messages = {'required': 'Please enter your password.'}

        self.error_messages['email_password_mismatch'] = 'The e-mail address and/or password you specified are not correct.'
        self.error_messages['username_password_mismatch'] = 'The e-mail address and/or password you specified are not correct.'