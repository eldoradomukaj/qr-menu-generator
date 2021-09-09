from copy import deepcopy

from django import forms
from django.db.models import Q
from restaurant.models import Category, Restaurant, RestaurantHours, Menu
from django.contrib.auth.models import User

class MenuForm(forms.ModelForm):
    image = forms.ImageField(required=False, label='', widget=forms.FileInput)
    
    class Meta:
        model = Menu
        fields = ('title', 'price', 'units', 'custom_unit', 'description', 'allergens', 'image_url', 'image')
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        return super(MenuForm, self).__init__(*args, **kwargs)
        self.fields['image'].label = ''

    def save(self, *args, **kwargs):
        kwargs['commit']=False
        obj = super(MenuForm, self).save(*args, **kwargs)
        if self.request:
            obj.user = self.request.user
        obj.save()
        return obj

class CategoryForm(forms.ModelForm):
    cat_name = forms.CharField(required=False)

    class Meta:
        model = Category
        fields = ('cat_name',)

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        self.fields['cat_name'].widget.attrs.update({'placeholder': 'Enter a category'})

class CategoryFormUpload(forms.ModelForm):
    cat_name = forms.CharField(required=True)
    cat_img = forms.ImageField(widget=forms.FileInput, required=False)

    class Meta:
        model = Category
        fields = ('cat_name', 'description', 'cat_img')

    def __init__(self, *args, **kwargs):
        super(CategoryFormUpload, self).__init__(*args, **kwargs)
        self.fields['cat_name'].widget.attrs.update({'placeholder': 'Enter a category'})
        self.fields['cat_name'].label = ' Category Name: '
        self.fields['cat_img'].label = ''

    #def clean(self):
    #    cleaned_data = self.cleaned_data
    #    cat_name = cleaned_data['cat_name']

    #    if cat_name and Category.objects.get(cat_name=cat_name):
    #        raise forms.ValidationError("Entry already exists")
    #    return cleaned_data


class RestaurantUpdateForm(forms.ModelForm):
    rest_logo = forms.ImageField(widget=forms.FileInput, required=False)

    class Meta:
        model = Restaurant
        fields = ('name', 'address1', 'address2', 'city', 'state', 'zipcode', 'phone', 'rest_logo')
    
    def __init__(self, *args, **kwargs):
        super(RestaurantUpdateForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = 'Restaurant Name'
        self.fields['address1'].label = 'Address Line 1'
        self.fields['address2'].label = 'Address Line 2'
        self.fields['rest_logo'].label = ''

class RestaurantHoursUpdateForm(forms.ModelForm):
    class Meta:
        model = RestaurantHours
        exclude = ['restaurant']

    def __init__(self, *args, **kwargs):
        self.prev_model = deepcopy(kwargs.get("instance"))
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

    def save(self):
        new_model = super().save(commit=False)

        new_model.monday_hours = new_model.monday_hours or self.prev_model.monday_hours
        new_model.tuesday_hours = new_model.tuesday_hours or self.prev_model.tuesday_hours
        new_model.wednesday_hours = new_model.wednesday_hours or self.prev_model.wednesday_hours
        new_model.thursday_hours = new_model.thursday_hours or self.prev_model.thursday_hours
        new_model.friday_hours = new_model.friday_hours or self.prev_model.friday_hours
        new_model.saturday_hours = new_model.saturday_hours or self.prev_model.saturday_hours
        new_model.sunday_hours = new_model.sunday_hours or self.prev_model.sunday_hours
        
        new_model.save()

