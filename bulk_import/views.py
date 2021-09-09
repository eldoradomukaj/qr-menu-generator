from typing import Any, Dict, List, TextIO
import csv

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, reverse

from .forms import BulkImportForm
from restaurant.models import Restaurant, Category, Menu


def process_category_upload(f: TextIO, restaurant: Restaurant) -> int:
    """
    Takes a CSV file a path `f` and adds the categories it describes to `restaurant`. Returns the number of categories added.
    """

    restaurant_categories: List[str] = [c.cat_name for c in Category.objects.filter(restaurant=restaurant)]

    reader = csv.DictReader(f.read().decode('utf-8').splitlines())
    count = 0

    for row in reader:
        new_cat: Category
        new_cat, _ = Category.objects.update_or_create(
            cat_name=row['Name'].lower(),
            restaurant=restaurant,
            defaults={
                'description': row.get('Description', ''),
            },
        )
        count += 1

    return count


def process_menu_upload(f: str, restaurant: Restaurant) -> int:
    """
    Takes a CSV file a path `f` and adds the menu items it describes to `restaurant`. Returns the number of items added.
    """

    # dict of {category name, category object}
    # acts as a cache so we don't have to do a query for each iteration
    restaurant_categories: Dict[str, Category] = {c.cat_name: c for c in Category.objects.filter(restaurant=restaurant)}

    reader: csv.DictReader = csv.DictReader(f.read().decode('utf-8').splitlines())
    count: int = 0

    for row in reader:
        if row["Category"].lower() not in restaurant_categories.keys():
            new_cat: Category = Category.objects.create(cat_name=row["Category"], restaurant=restaurant)
            new_cat.save()
            restaurant_categories[new_cat.cat_name] = new_cat

        new_item: Menu
        new_item_defaults: Dict[str, Any] = {
            'description': row.get("Description", ""),
            'image_url': row.get("Image URL", ""),
        }
        try:
            new_item_defaults['price'] = float(row["Price"])
        except ValueError:
            pass

        new_item, _ = Menu.objects.update_or_create(
            owner=restaurant,
            user=restaurant.owner,
            title=row["Menu Item"],
            category=restaurant_categories[row["Category"].lower()],
            defaults=new_item_defaults,
        )
        count += 1

    return count


@user_passes_test(lambda u: u.is_superuser)  # user must have admin privileges
def upload(request):
    if request.method == 'POST':
        form = BulkImportForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data.get('cat_file'):
                num_categories: int = process_category_upload(request.FILES['cat_file'], form.cleaned_data['restaurant'])
                messages.success(request, 'Successfully imported {} categories.'.format(str(num_categories)), extra_tags='cats')
            if form.cleaned_data.get('menu_file'):
                num_menus: int = process_menu_upload(request.FILES['menu_file'], form.cleaned_data['restaurant'])
                messages.success(request, 'Successfully imported {} menus.'.format(str(num_menus)), extra_tags='menus')
            return HttpResponseRedirect(reverse(
                'admin:restaurant_restaurant_change',
                args=(form.cleaned_data['restaurant'].cust_pk,),
            ))
    else:
        form = BulkImportForm(initial={
            'restaurant': Restaurant.objects.get(cust_pk=request.GET['id']),
        })
    
    context = {
        'form': form,
    }
    return render(request, "bulk_import/upload.html", context)
