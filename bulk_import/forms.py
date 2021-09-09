from typing import Dict, NoReturn

from django import forms

from restaurant.models import Restaurant


class BulkImportForm(forms.Form):
    restaurant = forms.ModelChoiceField(Restaurant.objects.all())
    cat_file = forms.FileField(required=False)
    menu_file = forms.FileField(required=False)

    def clean(self) -> NoReturn:
        """
        Checks that at least one of the two FileFields has been submitted.
        """
        cleaned_data: Dict = super().clean()
        cat_file = cleaned_data.get("cat_file")
        menu_file = cleaned_data.get("menu_file")
        if not (cat_file or menu_file):
            raise forms.ValidationError(
                "At least one file should be submitted."
            )
