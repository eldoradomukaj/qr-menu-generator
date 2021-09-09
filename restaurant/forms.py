from django import forms
from .models import Order


class BugReportForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(), required=True, label='message')
    browser_data = forms.CharField(widget=forms.HiddenInput(), required=False, label='browser_data')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].widget.attrs.update({
            'placeholder': 'Provide info about the issue and steps to reproduce.',
            'class': 'form-control',
        })


class RestaurantOrderForm(forms.ModelForm):
    name = forms.CharField(required=True)
    table_number = forms.IntegerField(required=True)

    class Meta:
        model = Order
        fields = ['name', 'table_number']
