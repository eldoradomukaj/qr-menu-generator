from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from restaurant.models import Restaurant
from localflavor.us.forms import USStateSelect, USZipCodeField, USStateField

class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True, label='email')
    name = forms.CharField(required=True, label='name')
    message = forms.CharField(widget=forms.Textarea(), required=True, label='message')

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['from_email'].widget.attrs.update({'placeholder': 'E-Mail'})
        self.fields['name'].widget.attrs.update({'placeholder': 'Name'})
        self.fields['message'].widget.attrs.update({'placeholder': 'Enter your message'})


class RestaurantForm(forms.ModelForm):
    name = forms.CharField(required=True)
    address1 = forms.CharField(required=True)
    city = forms.CharField(required=True)
    state = forms.CharField(widget=USStateSelect, required=True)
    
    class Meta:
        model = Restaurant
        fields = ('name', 'address1', 'address2', 'city', 'state', 'zipcode')

    def __init__(self, *args, **kwargs):
        super(RestaurantForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': 'Restaurant Name'})
        self.fields['address1'].widget.attrs.update({'placeholder': 'Address Line 1'})
        self.fields['address2'].widget.attrs.update({'placeholder': 'Address Line 2'})
        self.fields['city'].widget.attrs.update({'placeholder': 'City'})
        self.fields['zipcode'].widget.attrs.update({'placeholder': 'Zipcode'})

        self.fields['name'].error_messages = {'required': 'Please enter a restaurant name'}
        self.fields['address1'].error_messages = {'required': 'Please enter a address'}
        self.fields['address2'].error_messages = {'required': 'Please enter a address'}
        self.fields['city'].error_messages = {'required': 'Please enter a city'}
        self.fields['zipcode'].error_messages = {'required': 'Please enter a valid zip code'}


        for fieldname in ['name', 'address1', 'address2', 'city', 'state', 'zipcode']:
            self.fields[fieldname].label = ''